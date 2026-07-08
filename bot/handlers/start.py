# ===================================================================
# Wilson_AI Project
# Handler: /start Command
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... содержимое функции без изменений ...
    """Обработчик команды /start."""
    user_id = update.effective_user.id
    
    # Проверяем, что это разрешённый пользователь
    if user_id != context.bot_data["config"].USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    # Проверяем, есть ли уже пароль в сессии
    if context.user_data.get("authenticated", False):
        await update.message.reply_text(
            "👋 Привет! Я Wilson, твой цифровой друг.\n"
            "Я уже готов к разговору. Просто напиши мне что-нибудь!"
        )
    else:
        await update.message.reply_text(
            "🏐 Привет! Я Wilson.\n\n"
            "Я — твой добрый собеседник. Я помню наши разговоры, умею слушать и поддерживать.\n\n"
            "🔐 Для начала давай создадим пароль для твоей личной базы данных.\n"
            "**Придумай пароль и отправь его мне.**\n"
            "Этот пароль нужен только для того, чтобы защитить наши диалоги. Я его нигде не храню!"
        )
        # Переводим бота в режим ожидания пароля
        context.user_data["awaiting_password"] = True