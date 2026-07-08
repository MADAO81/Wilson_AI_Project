# ===================================================================
# Wilson_AI Project
# Configuration Loader
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Класс для хранения всех настроек бота."""
    
    # Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в .env!")
    
    USER_ID = int(os.getenv("USER_ID", 0))
    if USER_ID == 0:
        raise ValueError("USER_ID не задан в .env!")
    
    # DeepSeek (совместим с OpenAI)
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY не задан в .env!")
    
    DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # База данных
    DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/dialogues.db")
    
    # Сессия
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 30))  # минут
    
    # Системный промпт (личность бота)
    SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Ты — добрый и поддерживающий собеседник по имени Wilson.")
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Режим разработки
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Создаём экземпляр конфига для импорта в других модулях
config = Config()