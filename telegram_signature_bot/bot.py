import logging
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from .database import Database

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class SignatureBot:
    def __init__(self, token: str, db_name: str = 'signatures.db'):
        self.application = Application.builder().token(token).build()
        self.db = Database(db_name)
        self.setup_handlers()

    def setup_handlers(self) -> None:
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("set_signature", self.set_signature))
        self.application.add_handler(CommandHandler("remove_signature", self.remove_signature))
        self.application.add_handler(CommandHandler("show_signature", self.show_signature))
        self.application.add_handler(CommandHandler("set_channel", self.set_channel))
        self.application.add_handler(CommandHandler("remove_channel", self.remove_channel))
        self.application.add_handler(CommandHandler("show_channel", self.show_channel))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        await update.message.reply_text(
            'Привет! Я бот для автоматического добавления подписи к сообщениям.\n\n'
            'Доступные команды:\n'
            '/set_signature <подпись> - установить подпись\n'
            '/remove_signature - удалить подпись\n'
            '/show_signature - показать текущую подпись\n'
            '/set_channel @channel_name - установить канал для публикации\n'
            '/remove_channel - удалить канал\n'
            '/show_channel - показать текущий канал'
        )

    async def set_signature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Установка подписи пользователя"""
        if not context.args:
            await update.message.reply_text(
                'Пожалуйста, укажите подпись после команды.\n'
                'Пример: /set_signature С уважением, Иван'
            )
            return

        signature = ' '.join(context.args)
        user_id = update.effective_user.id
        self.db.set_signature(user_id, signature)
        await update.message.reply_text(f'Подпись установлена:\n{signature}')

    async def remove_signature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Удаление подписи пользователя"""
        user_id = update.effective_user.id
        signature = self.db.get_signature(user_id)
        if signature:
            self.db.remove_signature(user_id)
            await update.message.reply_text('Подпись удалена.')
        else:
            await update.message.reply_text('У вас нет установленной подписи.')

    async def show_signature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показ текущей подписи пользователя"""
        user_id = update.effective_user.id
        signature = self.db.get_signature(user_id)
        if signature:
            await update.message.reply_text(f'Ваша текущая подпись:\n{signature}')
        else:
            await update.message.reply_text('У вас нет установленной подписи.')

    async def set_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Установка канала для публикации"""
        if not context.args:
            await update.message.reply_text(
                'Пожалуйста, укажите ID канала после команды.\n'
                'Пример: /set_channel @mychannel'
            )
            return

        channel_id = context.args[0]
        user_id = update.effective_user.id

        try:
            # Проверяем, есть ли у бота доступ к каналу
            test_message = await context.bot.send_message(channel_id, "Тестовое сообщение")
            await context.bot.delete_message(channel_id, test_message.message_id)
            
            self.db.set_channel(user_id, channel_id)
            await update.message.reply_text(f'Канал {channel_id} успешно установлен.')
        except TelegramError as e:
            logger.error(f"Error setting channel for user {user_id}: {str(e)}")
            await update.message.reply_text(
                f'Ошибка при установке канала. Убедитесь, что:\n'
                f'1. Канал существует\n'
                f'2. Бот добавлен в канал как администратор\n'
                f'3. ID канала указан верно\n\n'
                f'Ошибка: {str(e)}'
            )

    async def remove_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Удаление канала"""
        user_id = update.effective_user.id
        channel = self.db.get_channel(user_id)
        if channel:
            self.db.remove_channel(user_id)
            await update.message.reply_text('Канал удален.')
        else:
            await update.message.reply_text('У вас нет установленного канала.')

    async def show_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показ текущего канала"""
        user_id = update.effective_user.id
        channel = self.db.get_channel(user_id)
        if channel:
            await update.message.reply_text(f'Ваш текущий канал: {channel}')
        else:
            await update.message.reply_text('У вас нет установленного канала.')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка входящих сообщений"""
        user_id = update.effective_user.id
        signature = self.db.get_signature(user_id)
        channel = self.db.get_channel(user_id)
        
        if signature:
            message_with_signature = f"{update.message.text}\n\n{signature}"
            
            # Отправляем сообщение в ответ пользователю
            await update.message.reply_text(message_with_signature)
            
            # Если установлен канал, отправляем сообщение в канал
            if channel:
                try:
                    await context.bot.send_message(channel, message_with_signature)
                except TelegramError as e:
                    logger.error(f"Error sending message to channel {channel}: {str(e)}")
                    await update.message.reply_text(
                        f'Ошибка при отправке в канал {channel}. '
                        f'Проверьте права бота и существование канала.\n'
                        f'Ошибка: {str(e)}'
                    )

    def run(self) -> None:
        """Запуск бота"""
        self.application.run_polling()