import sqlite3
from typing import Optional

class Database:
    def __init__(self, db_name: str = 'signatures.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self) -> None:
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Таблица для подписей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signatures (
                    user_id INTEGER PRIMARY KEY,
                    signature TEXT NOT NULL
                )
            ''')
            # Таблица для каналов пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    user_id INTEGER,
                    channel_id TEXT NOT NULL,
                    PRIMARY KEY (user_id, channel_id)
                )
            ''')
            conn.commit()

    def set_signature(self, user_id: int, signature: str) -> None:
        """Сохранение подписи пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO signatures (user_id, signature)
                VALUES (?, ?)
            ''', (user_id, signature))
            conn.commit()

    def get_signature(self, user_id: int) -> Optional[str]:
        """Получение подписи пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT signature FROM signatures WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def remove_signature(self, user_id: int) -> None:
        """Удаление подписи пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM signatures WHERE user_id = ?', (user_id,))
            conn.commit()

    def set_channel(self, user_id: int, channel_id: str) -> None:
        """Сохранение канала пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO channels (user_id, channel_id)
                VALUES (?, ?)
            ''', (user_id, channel_id))
            conn.commit()

    def get_channel(self, user_id: int) -> Optional[str]:
        """Получение канала пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT channel_id FROM channels WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def remove_channel(self, user_id: int) -> None:
        """Удаление канала пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM channels WHERE user_id = ?', (user_id,))
            conn.commit()