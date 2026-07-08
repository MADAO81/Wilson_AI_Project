# Wilson AI — твой цифровой друг 🏐

Wilson — это Telegram-бот на базе DeepSeek, созданный для дружеского общения и поддержки.  
Он помнит тебя, умеет слушать (голосовые сообщения), смотреть (анализ изображений) и отвечать как живой собеседник.

---

## 🚀 Быстрый старт

### 1. Клонируй репозиторий
```bash
git clone https://github.com/MADAO81/Wilson_AI_Project.git
cd Wilson_AI_Project
```

### 2. Создай виртуальное окружение
```bash
python3 -m venv venv
source venv/bin/activate  # для Linux/Mac
# venv\Scripts\activate   # для Windows
```

### 3. Установи зависимости
```bash
pip install -r requirements.txt
```

### 4. Создай файл `.env` (см. `.env.example`)
```env
BOT_TOKEN=ваш_токен_бота
USER_ID=ваш_telegram_id
DEEPSEEK_API_KEY=ваш_ключ_DeepSeek
SYSTEM_PROMPT="Ты — добрый и поддерживающий собеседник."
DATABASE_PATH=./data/dialogues.db
SESSION_TIMEOUT=30
```

### 5. Запусти бота
```bash
python bot/main.py
```

---

## 🧠 Возможности
* **✅ Текстовое общение** с DeepSeek
* **✅ Долговременная память** (SQLCipher)
* **✅ Защита паролем** базы данных
* **✅ Голосовые сообщения** → распознавание в текст
* **✅ Анализ изображений** (DeepSeek Vision)
* **✅ Удобные команды**: `/start`, `/help`, `/clear`, `/reset`

---

## 🛡️ Безопасность
* Все данные хранятся в зашифрованной базе (**SQLCipher**).
* Пароль вводит пользователь, бот его не хранит.
* Сессия автоматически завершается через **15–30 минут**.
* Поддержка команды `/clear` с обязательным подтверждением паролем.

---

## 📁 Структура проекта
```text
Wilson_AI_Project/
├── bot/
│   ├── main.py
│   ├── config.py
│   ├── handlers/
│   │   ├── start.py
│   │   ├── help.py
│   │   └── clear.py
│   ├── database/
│   │   └── db_manager.py
│   └── utils/
│       └── logger.py
├── data/                  # База данных (не в Git)
├── .env                   # Секреты (не в Git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📜 Лицензия
**MIT** — используй как хочешь, но с душой. 😉

---
🏐 *Wilson всегда с тобой.*
