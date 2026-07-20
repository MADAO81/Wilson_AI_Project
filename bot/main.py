# ===================================================================
# Wilson_AI Project
# Core Bot Application with DeepSeek via OpenRouter (ProxyAPI)
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

import logging
import os
from datetime import datetime, timedelta
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
    """Отправка запроса к DeepSeek через OpenRouter (ProxyAPI)."""
    try:
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT}
        ]
        for role, content in history[-10:]:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})
        
        response = await deepseek_client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.9,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Ошибка при обращении к DeepSeek через OpenRouter: {e}")
        return "😅 Извини, я сейчас не могу ответить. Попробуй позже."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений с логикой 'придумать/ввести пароль' и таймаутом."""
    user_id = update.effective_user.id
    
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    # --- ПРОВЕРКА ТАЙМАУТА СЕССИИ ---
    if context.user_data.get("authenticated", False):
        last_activity = context.user_data.get("last_activity")
        if last_activity:
            # Проверяем, не истекло ли время сессии
            time_diff = datetime.now() - last_activity
            if time_diff > timedelta(minutes=config.SESSION_TIMEOUT):
                # Сессия истекла
                context.user_data["authenticated"] = False
                context.user_data["awaiting_password"] = True
                # Закрываем соединение с базой, если оно было открыто
                db = context.bot_data["db_manager"]
                db.close()
                await update.message.reply_text(
                    f"⏰ Сессия истекла ({config.SESSION_TIMEOUT} минут бездействия).\n"
                    "Введи пароль заново, чтобы продолжить."
                )
                return
        # Обновляем время последней активности
        context.user_data["last_activity"] = datetime.now()
    
    # --- ЛОГИКА АВТОРИЗАЦИИ ---
    if not context.user_data.get("authenticated", False):
        db_manager = context.bot_data["db_manager"]
        
        # Проверяем, существует ли база данных
        db_exists = os.path.exists(db_manager.db_path)
        
        # Если пользователь уже вводит пароль (мы ждём его)
        if context.user_data.get("awaiting_password", False):
            password = update.message.text.strip()
            
            if not password:
                await update.message.reply_text("❌ Пароль не может быть пустым. Попробуй ещё раз.")
                return
            
            # Пытаемся открыть базу с этим паролем
            if db_manager.connect(password):
                context.user_data["password"] = password
                context.user_data["authenticated"] = True
                context.user_data["awaiting_password"] = False
                context.user_data["last_activity"] = datetime.now()
                
                await update.message.reply_text(
                    "✅ Пароль принят! База данных открыта.\n"
                    "Рад снова тебя видеть! 😊"
                )
            else:
                await update.message.reply_text(
                    "❌ Неверный пароль. Попробуй ещё раз или напиши /start, чтобы начать заново."
                )
            return
        
        # Если пароль ещё не вводили — определяем, что показать
        if db_exists:
            # База уже есть — просим ввести пароль
            await update.message.reply_text(
                "🔐 Я тебя помню! Введи свой пароль, чтобы открыть базу данных.\n"
                "Если забыл пароль — напиши /reset, чтобы начать заново."
            )
            context.user_data["awaiting_password"] = True
            return
        else:
            # Базы нет — это новый пользователь, просим придумать пароль
            await update.message.reply_text(
                "🏐 Привет! Ты здесь впервые.\n\n"
                "Давай создадим пароль для твоей личной базы данных.\n"
                "**Придумай пароль и отправь его мне.**\n"
                "Этот пароль нужен только для того, чтобы защитить наши диалоги. Я его нигде не храню!",
                parse_mode="Markdown"
            )
            context.user_data["awaiting_password"] = True
            return
    
    # --- ОСНОВНАЯ ЛОГИКА ДЛЯ АВТОРИЗОВАННОГО ПОЛЬЗОВАТЕЛЯ ---
    user_message = update.message.text
    
    await update.message.chat.send_action(action="typing")
    
    try:
        db = context.bot_data["db_manager"]
        history = db.get_history(limit=10)
        
        bot_response = await get_deepseek_response(user_message, history)
        
        db.save_message("user", user_message)
        db.save_message("assistant", bot_response)
        
        await update.message.reply_text(bot_response)
        
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await update.message.reply_text(
            "😅 Произошла ошибка. Попробуй еще раз."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений."""
    user_id = update.effective_user.id
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа.")
        return
    
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text("🔐 Сначала введи пароль.")
        return
    
    await update.message.reply_text("🎤 Голосовые сообщения пока не поддерживаются, но скоро появятся!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик изображений."""
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
    
    # Создаём папку для базы данных, если её нет
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    
    db_manager = DatabaseManager(config.DATABASE_PATH)
    
    deepseek_client = AsyncOpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )
    
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    application.bot_data["db_manager"] = db_manager
    application.bot_data["config"] = config
    application.bot_data["deepseek_client"] = deepseek_client
    
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", help.help_command))
    application.add_handler(CommandHandler("clear", clear.clear_command))
    application.add_handler(CommandHandler("reset", reset.reset_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    application.add_error_handler(error_handler)
    
    logger.info("🚀 Wilson запускается с DeepSeek через OpenRouter...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
