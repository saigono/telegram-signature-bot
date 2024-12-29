import os
import pytest
from telegram_signature_bot.database import Database

@pytest.fixture
def test_db():
    """Фикстура для создания тестовой базы данных"""
    db_name = "test_signatures.db"
    db = Database(db_name)
    yield db
    # Очищаем после тестов
    if os.path.exists(db_name):
        os.remove(db_name)

def test_signature_operations(test_db):
    """Тест операций с подписями"""
    user_id = 12345
    signature = "Test Signature"
    
    # Проверяем, что изначально подписи нет
    assert test_db.get_signature(user_id) is None
    
    # Добавляем подпись
    test_db.set_signature(user_id, signature)
    assert test_db.get_signature(user_id) == signature
    
    # Обновляем подпись
    new_signature = "Updated Signature"
    test_db.set_signature(user_id, new_signature)
    assert test_db.get_signature(user_id) == new_signature
    
    # Удаляем подпись
    test_db.remove_signature(user_id)
    assert test_db.get_signature(user_id) is None

def test_channel_operations(test_db):
    """Тест операций с каналами"""
    user_id = 12345
    channel_id = "@test_channel"
    
    # Проверяем, что изначально канала нет
    assert test_db.get_channel(user_id) is None
    
    # Добавляем канал
    test_db.set_channel(user_id, channel_id)
    assert test_db.get_channel(user_id) == channel_id
    
    # Обновляем канал
    new_channel = "@new_channel"
    test_db.set_channel(user_id, new_channel)
    assert test_db.get_channel(user_id) == new_channel
    
    # Удаляем канал
    test_db.remove_channel(user_id)
    assert test_db.get_channel(user_id) is None

def test_multiple_users(test_db):
    """Тест работы с несколькими пользователями"""
    user1_id = 111
    user2_id = 222
    signature1 = "Signature 1"
    signature2 = "Signature 2"
    channel1 = "@channel1"
    channel2 = "@channel2"
    
    # Добавляем данные для обоих пользователей
    test_db.set_signature(user1_id, signature1)
    test_db.set_signature(user2_id, signature2)
    test_db.set_channel(user1_id, channel1)
    test_db.set_channel(user2_id, channel2)
    
    # Проверяем, что данные не перемешиваются
    assert test_db.get_signature(user1_id) == signature1
    assert test_db.get_signature(user2_id) == signature2
    assert test_db.get_channel(user1_id) == channel1
    assert test_db.get_channel(user2_id) == channel2
