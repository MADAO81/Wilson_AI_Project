# ===================================================================
# Wilson_AI Project
# Core Bot Application
# Author: MADAO81 (https://github.com/MADAO81)
# Description: Main entry point for the Wilson Telegram bot.
# ===================================================================

import logging
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

# Глобальный менеджер базы данных (будет инициализирован после запуска)
db_manager = None

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок."""
    logger.error(f"Ошибка: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😅 Что-то пошло не так. Попробуй еще раз или напиши /help."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений."""
    user_id = update.effective_user.id
    
    # Проверяем, что это разрешённый пользователь
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    # Проверяем, что сессия активна (пароль введён)
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text(
            "🔐 Пожалуйста, введи пароль для доступа к твоим диалогам.\n"
            "Если ты новый пользователь — придумай пароль и отправь его."
        )
        return
    
    # Получаем сообщение пользователя
    user_message = update.message.text
    
    # TODO: Здесь будет интеграция с DeepSeek
    # 1. Получить историю диалога из БД
    # 2. Отправить запрос в DeepSeek
    # 3. Сохранить ответ в БД
    # 4. Отправить ответ пользователю
    
    # Временный ответ (заглушка)
    await update.message.reply_text(
        f"🧠 Я Wilson. Ты написал: «{user_message}»\n"
        "Пока я учусь отвечать, но скоро я стану настоящим другом!"
    )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений."""
    user_id = update.effective_user.id
    
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text("🔐 Пожалуйста, введи пароль для доступа к диалогам.")
        return
    
    # TODO: Интеграция с DeepSeek ASR (распознавание речи)
    await update.message.reply_text("🎤 Я получил твоё голосовое сообщение. Скоро я научусь его понимать!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик изображений."""
    user_id = update.effective_user.id
    
    if user_id != config.USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text("🔐 Пожалуйста, введи пароль для доступа к диалогам.")
        return
    
    # TODO: Интеграция с DeepSeek Vision (анализ изображений)
    await update.message.reply_text("🖼️ Я получил твою картинку. Скоро я научусь её описывать!")

def main():
    """Запуск бота."""
    global db_manager
    
    # Инициализируем базу данных
    db_manager = DatabaseManager(config.DATABASE_PATH)
    
    # Создаём приложение
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Сохраняем db_manager и config в контексте приложения для доступа из хендлеров
    application.bot_data["db_manager"] = db_manager
    application.bot_data["config"] = config  # <--- ЭТА СТРОКА ДОБАВЛЕНА
    
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
    logger.info("🚀 Wilson запускается...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
