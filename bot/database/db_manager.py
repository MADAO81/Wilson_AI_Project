# ===================================================================
# Wilson_AI Project
# Database Manager (SQLCipher)
# Author: MADAO81 (https://github.com/MADAO81)
# ===================================================================

import sqlite3
import os
from datetime import datetime, timedelta

class DatabaseManager:
    """Менеджер для работы с зашифрованной базой данных SQLCipher."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self.password = None
        
        # Создаём папку для базы, если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    def connect(self, password):
        """Подключение к базе данных с паролем."""
        try:
            # Подключаемся к SQLite
            self.connection = sqlite3.connect(self.db_path)
            # Устанавливаем пароль для SQLCipher
            self.connection.execute(f"PRAGMA key='{password}'")
            # Включаем внешние ключи
            self.connection.execute("PRAGMA foreign_keys = ON")
            
            # Проверяем, что база открылась (создаём таблицы, если их нет)
            self._init_db()
            self.password = password
            return True
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return False
    
    def _init_db(self):
        """Создание таблиц, если их нет."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON conversations(timestamp)
        """)
        self.connection.commit()
    
    def save_message(self, role, content, session_id=None):
        """Сохранить сообщение в базу."""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO conversations (role, content, session_id)
            VALUES (?, ?, ?)
        """, (role, content, session_id))
        self.connection.commit()
        return cursor.lastrowid
    
    def get_history(self, limit=20):
        """Получить последние N сообщений."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT role, content FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        # Возвращаем в хронологическом порядке
        return list(reversed(rows))
    
    def clear_history(self):
        """Удалить всю историю."""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM conversations")
        self.connection.commit()
    
    def close(self):
        """Закрыть соединение с базой."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.password = None