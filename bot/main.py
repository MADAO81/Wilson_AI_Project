# ===================================================================
# Wilson_AI Project
# Core Bot Application with DeepSeek via ProxyAPI
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

import logging
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import config
from database.db_manager import DatabaseManager
from handlers import start, help, clear, reset

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# Глобальные переменные
db_manager = None
deepseek_client = None

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок."""
    logger.error(f"Ошибка: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😅 Что-то пошло не так. Попробуй еще раз или напиши /help."
        )

async def get_deepseek_response(user_message: str, history: list) -> str:
    """Отправка запроса к DeepSeek через ProxyAPI и получение ответа."""
    try:
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT}
        ]
        # Добавляем историю (до 10 последних сообщений)
        for role, content in history[-10:]:
            messages.append({"role": role, "content": content})
        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})
        
        # Отправляем запрос к DeepSeek через ProxyAPI
        response = await deepseek_client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при обращении к DeepSeek через ProxyAPI: {e}")
        return "😅 Извини, я сейчас не могу ответить. Попробуй позже."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений."""
    user_id = update.effective_user.id
    
    # Проверяем доступ
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    # Проверяем авторизацию
    if not context.user_data.get("authenticated", False):
        # Обработка пароля
        if context.user_data.get("awaiting_password", False):
            password = update.message.text.strip()
            if not password:
                await update.message.reply_text("❌ Пароль не может быть пустым.")
                return
            
            context.user_data["password"] = password
            context.user_data["authenticated"] = True
            context.user_data["awaiting_password"] = False
            
            db_manager = context.bot_data["db_manager"]
            if db_manager.connect(password):
                await update.message.reply_text(
                    "✅ Пароль принят! Твоя база данных открыта.\n"
                    "Теперь мы можем общаться. Просто напиши мне что-нибудь!"
                )
            else:
                context.user_data["authenticated"] = False
                await update.message.reply_text(
                    "❌ Не удалось открыть базу данных. Возможно, пароль неверный.\n"
                    "Попробуй ещё раз или напиши /start."
                )
            return
        else:
            context.user_data["awaiting_password"] = True
            await update.message.reply_text(
                "🔐 Придумай и отправь мне пароль для твоей базы данных.\n"
                "Он будет использоваться для шифрования твоих диалогов."
            )
            return
    
    # --- Основная логика для авторизованного пользователя ---
    user_message = update.message.text
    
    # Отправляем статус "печатает"
    await update.message.chat.send_action(action="typing")
    
    try:
        # Получаем историю из базы данных
        db = context.bot_data["db_manager"]
        history = db.get_history(limit=10)
        
        # Получаем ответ от DeepSeek через ProxyAPI
        bot_response = await get_deepseek_response(user_message, history)
        
        # Сохраняем диалог в базу
        db.save_message("user", user_message)
        db.save_message("assistant", bot_response)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await update.message.reply_text(
            "😅 Произошла ошибка. Попробуй еще раз."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений (заглушка)."""
    user_id = update.effective_user.id
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа.")
        return
    
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text("🔐 Сначала введи пароль.")
        return
    
    await update.message.reply_text("🎤 Голосовые сообщения пока не поддерживаются, но скоро появятся!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик изображений (заглушка)."""
    user_id = update.effective_user.id
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа.")
        return
    
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text("🔐 Сначала введи пароль.")
        return
    
    await update.message.reply_text("🖼️ Анализ изображений пока не поддерживается, но скоро появится!")

def main():
    """Запуск бота."""
    global db_manager, deepseek_client
    
    # Инициализируем менеджер базы данных
    db_manager = DatabaseManager(config.DATABASE_PATH)
    
    # Инициализируем клиента DeepSeek через ProxyAPI
    deepseek_client = AsyncOpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )
    
    # Создаём приложение
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Сохраняем зависимости
    application.bot_data["db_manager"] = db_manager
    application.bot_data["config"] = config
    application.bot_data["deepseek_client"] = deepseek_client
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", help.help_command))
    application.add_handler(CommandHandler("clear", clear.clear_command))
    application.add_handler(CommandHandler("reset", reset.reset_command))
    
    # Регистрируем обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("🚀 Wilson запускается с DeepSeek через ProxyAPI...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
