import logging
from typing import Optional, List
from telegram import Update, MessageEntity
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
            '/set_signature <подпись> - установить подпись (поддерживается форматирование)\n'
            '/remove_signature - удалить подпись\n'
            '/show_signature - показать текущую подпись\n'
            '/set_channel @channel_name - установить канал для публикации\n'
            '/remove_channel - удалить канал\n'
            '/show_channel - показать текущий канал'
        )

    def extract_signature_entities(self, message: str, original_entities: List[MessageEntity], 
                                 start_index: int) -> List[MessageEntity]:
        """Извлекает entities для подписи из сообщения"""
        signature_entities = []
        for entity in original_entities:
            # Проверяем, относится ли entity к тексту подписи
            if entity.offset >= start_index:
                # Создаем новый entity с обновленным смещением
                new_offset = entity.offset - start_index

                # Для ссылок просто используем MessageEntity с типом TEXT_LINK
                new_entity = MessageEntity(
                    type=entity.type,
                    offset=new_offset,
                    length=entity.length,
                    url=entity.url if entity.type == MessageEntity.TEXT_LINK else None
                )
                signature_entities.append(new_entity)
        return signature_entities

    async def set_signature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Установка подписи пользователя"""
        if not context.args:
            await update.message.reply_text(
                'Пожалуйста, укажите подпись после команды.\n'
                'Пример: /set_signature С уважением, Иван\n\n'
                'Поддерживается форматирование текста (выделение жирным, курсивом, ссылки и т.д.)'
            )
            return

        # Получаем текст подписи и его форматирование
        full_message = update.message.text
        command_end = full_message.find(' ')
        if command_end == -1:
            signature = ''
            signature_entities = []
        else:
            signature = full_message[command_end + 1:]
            signature_entities = self.extract_signature_entities(
                full_message, 
                update.message.entities or [], 
                command_end + 1
            )

        user_id = update.effective_user.id
        self.db.set_signature(user_id, signature, signature_entities)
        
        # Показываем сохраненную подпись с форматированием
        message_prefix = 'Подпись установлена:\n'
        await update.message.reply_text(
            f'{message_prefix}{signature}',
            entities=[MessageEntity(
                        type=e.type,
                        offset=e.offset + len(message_prefix),
                        length=e.length,
                        url=e.url if e.type == MessageEntity.TEXT_LINK else None
                    ) for e in signature_entities]
        )

    async def show_signature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показ текущей подписи пользователя"""
        user_id = update.effective_user.id
        signature, entities = self.db.get_signature(user_id)
        message_prefix = 'Ваша текущая подпись:\n'

        if signature:
            # Преобразуем сохраненные entities обратно в объекты MessageEntity
            telegram_entities = []
            if entities:
                for e in entities:
                    entity = MessageEntity(
                        type=e['type'],
                        offset=e['offset'] + len(message_prefix),
                        length=e['length'],
                        url=e.get('url')
                    )
                    telegram_entities.append(entity)
            
            await update.message.reply_text(
                f'{message_prefix}{signature}',
                entities=telegram_entities
            )
        else:
            await update.message.reply_text('У вас нет установленной подписи.')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка входящих сообщений"""
        user_id = update.effective_user.id
        signature, signature_entities = self.db.get_signature(user_id)
        channel = self.db.get_channel(user_id)
        
        if signature:
            # Копируем оригинальное сообщение и его форматирование
            original_message = update.message.text or ""
            original_entities = list(update.message.entities or [])
            
            # Добавляем подпись с переносом строк
            message_with_signature = f"{original_message}\n\n{signature}"
            
            # Объединяем entities из сообщения и подписи
            combined_entities = list(original_entities)
            if signature_entities:
                # Преобразуем сохраненные entities подписи
                for e in signature_entities:
                    new_offset = e['offset'] + len(original_message) + 2
                    entity = MessageEntity(
                        type=e['type'],
                        offset=new_offset,
                        length=e['length'],
                        url=e.get('url')
                    )
                    combined_entities.append(entity)
            
            # Отправляем сообщение пользователю
            await update.message.reply_text(
                message_with_signature,
                entities=combined_entities
            )
            
            # Отправляем в канал, если он установлен
            if channel:
                try:
                    await context.bot.send_message(
                        channel,
                        message_with_signature,
                        entities=combined_entities
                    )
                except TelegramError as e:
                    logger.error(f"Error sending message to channel {channel}: {str(e)}")
                    await update.message.reply_text(
                        f'Ошибка при отправке в канал {channel}. '
                        f'Проверьте права бота и существование канала.\n'
                        f'Ошибка: {str(e)}'
                    )

    async def remove_signature(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Удаление подписи пользователя"""
        user_id = update.effective_user.id
        signature = self.db.get_signature(user_id)
        if signature:
            self.db.remove_signature(user_id)
            await update.message.reply_text('Подпись удалена.')
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

    def run(self) -> None:
        """Запуск бота"""
        self.application.run_polling()
