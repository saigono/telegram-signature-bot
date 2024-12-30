import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .bot import SignatureBot


def load_environment():
    """Загрузка переменных окружения"""
    # Загружаем .env файл
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    # Проверяем наличие требуемых переменных
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)


def main() -> None:
    """Основная функция для запуска бота"""
    # Загружаем переменные окружения
    load_environment()

    # Настройка логирования
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level),
    )

    logger = logging.getLogger(__name__)

    try:
        # Получаем токен
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        # Определяем путь к базе данных
        env = os.getenv("ENVIRONMENT", "development")
        data_dir = Path.home() / "telegram-signature-bot" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = str(data_dir / f"{env}.db")

        # Инициализируем и запускаем бота
        bot = SignatureBot(token, db_path)
        logger.info(f"Бот запущен с базой данных {db_path}")
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
