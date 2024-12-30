from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Update
from telegram.ext import ContextTypes

from telegram_signature_bot.bot import SignatureBot


@pytest.fixture
def mock_update():
    """Фикстура для создания мока Update"""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock()
    update.effective_user.id = 12345
    update.message = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Фикстура для создания мока Context"""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    return context


@pytest.fixture
def bot():
    """Фикстура для создания экземпляра бота"""
    return SignatureBot("test_token", "test_signatures.db")


@pytest.mark.asyncio
async def test_start_command(bot, mock_update, mock_context):
    """Тест команды /start"""
    await bot.start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert "Привет!" in call_args
    assert "/set_signature" in call_args


@pytest.mark.asyncio
async def test_set_signature_command(bot, mock_update, mock_context):
    """Тест установки подписи"""
    # Тест без аргументов
    mock_context.args = []
    await bot.set_signature(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(
        "Пожалуйста, укажите подпись после команды.\n" "Пример: /set_signature С уважением, Иван"
    )

    # Тест с подписью
    mock_context.args = ["Тестовая", "подпись"]
    await bot.set_signature(mock_update, mock_context)
    assert bot.db.get_signature(mock_update.effective_user.id) == "Тестовая подпись"


@pytest.mark.asyncio
async def test_handle_message(bot, mock_update, mock_context):
    """Тест обработки обычных сообщений"""
    # Установка тестовой подписи
    user_id = mock_update.effective_user.id
    test_signature = "Тестовая подпись"
    bot.db.set_signature(user_id, test_signature)

    # Тестовое сообщение
    mock_update.message.text = "Тестовое сообщение"

    # Проверяем отправку сообщения с подписью
    await bot.handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_with(f"Тестовое сообщение\n\n{test_signature}")


@pytest.mark.asyncio
async def test_set_channel_command(bot, mock_update, mock_context):
    """Тест установки канала"""
    test_channel = "@test_channel"
    mock_context.args = [test_channel]

    # Мокаем успешную отправку тестового сообщения
    test_message = MagicMock()
    test_message.message_id = 1
    mock_context.bot.send_message.return_value = test_message

    await bot.set_channel(mock_update, mock_context)

    # Проверяем, что канал был установлен
    assert bot.db.get_channel(mock_update.effective_user.id) == test_channel

    # Проверяем, что было отправлено и удалено тестовое сообщение
    mock_context.bot.send_message.assert_called_with(test_channel, "Тестовое сообщение")
    mock_context.bot.delete_message.assert_called_with(test_channel, test_message.message_id)


@pytest.mark.asyncio
async def test_remove_signature_command(bot, mock_update, mock_context):
    """Тест удаления подписи"""
    user_id = mock_update.effective_user.id

    # Сброс состояния мока перед каждым тестом
    mock_update.message.reply_text.reset_mock()

    # Тест когда подписи нет
    await bot.remove_signature(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("У вас нет установленной подписи.")

    # Сброс состояния мока перед вторым тестом
    mock_update.message.reply_text.reset_mock()

    # Тест удаления существующей подписи
    bot.db.set_signature(user_id, "Тест")
    await bot.remove_signature(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once_with("Подпись удалена.")
    assert bot.db.get_signature(user_id) is None
