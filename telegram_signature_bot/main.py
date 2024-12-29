import os
import sys
import logging
from .bot import SignatureBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main() -> None:
    """Основная функция для запуска бота"""
    # Получаем токен из переменной окружения или аргументов командной строки
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token and len(sys.argv) > 1:
        token = sys.argv[1]
    
    if not token:
        logger.error("Токен бота не найден. Установите переменную окружения TELEGRAM_BOT_TOKEN "
                    "или передайте токен первым аргументом командной строки.")
        sys.exit(1)

    try:
        # Инициализируем и запускаем бота
        bot = SignatureBot(token)
        logger.info("Бот запущен")
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()