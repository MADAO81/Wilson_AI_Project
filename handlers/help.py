# ===================================================================
# Wilson_AI Project
# Handler: /help Command
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    user_id = update.effective_user.id
    
    if user_id != context.bot_data["config"].USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    help_text = (
        "🧠 **Wilson — твой цифровой друг**\n\n"
        "**Команды:**\n"
        "/start — начать общение (или перезапустить)\n"
        "/help — показать это сообщение\n"
        "/clear — удалить всю историю диалогов (с подтверждением пароля)\n"
        "/reset — полное обнуление (забыть пользователя)\n\n"
        "**Возможности:**\n"
        "📝 Текстовые сообщения — я отвечаю на них\n"
        "🎤 Голосовые сообщения — я учусь их распознавать\n"
        "🖼️ Изображения — я учусь их описывать\n\n"
        "🔐 Все диалоги хранятся в зашифрованной базе данных.\n"
        "Только ты знаешь пароль от неё."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")