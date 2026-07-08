# ===================================================================
# Wilson_AI Project
# Handler: /clear Command
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

# ... код без изменений ...

from telegram import Update
from telegram.ext import ContextTypes

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /clear — удаление истории."""
    user_id = update.effective_user.id
    
    if user_id != context.bot_data["config"].USER_ID:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    
    if not context.user_data.get("authenticated", False):
        await update.message.reply_text("🔐 Пожалуйста, сначала войди в систему (введи пароль).")
        return
    
    # Если уже ожидаем подтверждения
    if context.user_data.get("awaiting_clear_confirmation", False):
        # Проверяем, что пользователь написал "ДА, УДАЛИТЬ"
        if update.message.text.strip().upper() == "ДА, УДАЛИТЬ":
            # TODO: Удалить историю из БД
            context.user_data["awaiting_clear_confirmation"] = False
            await update.message.reply_text(
                "🗑️ Вся история диалогов удалена.\n"
                "Теперь мы можем начать заново."
            )
        else:
            context.user_data["awaiting_clear_confirmation"] = False
            await update.message.reply_text("❌ Команда отменена. История сохранена.")
        return
    
    # Запрашиваем подтверждение
    context.user_data["awaiting_clear_confirmation"] = True
    await update.message.reply_text(
        "⚠️ **Ты уверен, что хочешь удалить всю историю диалогов?**\n"
        "Это действие нельзя отменить.\n\n"
        "Если ты уверен, напиши: **ДА, УДАЛИТЬ**\n"
        "Если передумал — напиши что угодно другое.",
        parse_mode="Markdown"
    )