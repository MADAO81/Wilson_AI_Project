# ===================================================================
# Wilson_AI Project
# Handler: /reset Command (Full User Reset)
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

from telegram import Update
from telegram.ext import ContextTypes

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /reset — полное обнуление."""
    user_id = update.effective_user.id
    
    if user_id != context.bot_data["config"].USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    # Запрашиваем подтверждение с безопасным ключевым словом
    await update.message.reply_text(
        "⚠️ **Ты собираешься полностью обнулить себя в системе.**\n\n"
        "Будет удалена вся история диалогов, и я перестану тебя узнавать.\n"
        "При следующем обращении я попрошу создать новый пароль.\n\n"
        "Если ты уверен, напиши: **DELETE**\n"
        "Если передумал — напиши что угодно другое.",
        parse_mode="Markdown"
    )
    context.user_data["awaiting_reset_confirmation"] = True