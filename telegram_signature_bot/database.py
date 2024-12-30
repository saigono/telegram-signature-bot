import json
import sqlite3
from typing import List, Optional, Tuple

from telegram import MessageEntity


class Database:
    def __init__(self, db_name: str = "signatures.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self) -> None:
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Таблица для подписей
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS signatures (
                    user_id INTEGER PRIMARY KEY,
                    signature TEXT NOT NULL,
                    entities TEXT
                )
            """
            )
            # Таблица для каналов пользователей
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS channels (
                    user_id INTEGER,
                    channel_id TEXT NOT NULL,
                    PRIMARY KEY (user_id, channel_id)
                )
            """
            )
            conn.commit()

    def set_signature(
        self, user_id: int, signature: str, entities: Optional[List[MessageEntity]] = None
    ) -> None:
        """Сохранение подписи пользователя с форматированием"""
        # Конвертируем entities в JSON-совместимый формат
        entities_json = None
        if entities:
            entities_dict = [
                {
                    "type": entity.type,
                    "offset": entity.offset,
                    "length": entity.length,
                    "url": getattr(entity, "url", None),  # Для TEXT_LINK
                }
                for entity in entities
            ]
            entities_json = json.dumps(entities_dict)

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO signatures (user_id, signature, entities)
                VALUES (?, ?, ?)
            """,
                (user_id, signature, entities_json),
            )
            conn.commit()

    def get_signature(self, user_id: int) -> Tuple[Optional[str], Optional[List[dict]]]:
        """Получение подписи пользователя вместе с форматированием"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT signature, entities FROM signatures WHERE user_id = ?", (user_id,)
            )
            result = cursor.fetchone()

            if not result:
                return None, None

            signature, entities_json = result
            entities = json.loads(entities_json) if entities_json else None
            return signature, entities

    def remove_signature(self, user_id: int) -> None:
        """Удаление подписи пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM signatures WHERE user_id = ?", (user_id,))
            conn.commit()

    def set_channel(self, user_id: int, channel_id: str) -> None:
        """Сохранение канала пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO channels (user_id, channel_id)
                VALUES (?, ?)
            """,
                (user_id, channel_id),
            )
            conn.commit()

    def get_channel(self, user_id: int) -> Optional[str]:
        """Получение канала пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT channel_id FROM channels WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def remove_channel(self, user_id: int) -> None:
        """Удаление канала пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM channels WHERE user_id = ?", (user_id,))
            conn.commit()
