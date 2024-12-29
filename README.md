# Telegram Signature Bot

Telegram бот для автоматического добавления подписи к сообщениям и публикации в каналах. Бот позволяет установить персональную подпись, которая будет автоматически добавляться к вашим сообщениям, а также настроить автоматическую публикацию сообщений в указанном канале.

## Возможности

- Установка персональной подписи для сообщений
- Автоматическое добавление подписи к каждому сообщению
- Привязка к Telegram-каналу для автоматической публикации
- Сохранение настроек в SQLite базе данных
- Поддержка нескольких пользователей

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/telegram-signature-bot.git
cd telegram-signature-bot
```

2. Установите Poetry (если еще не установлен):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Установите зависимости:
```bash
poetry install
```

## Настройка

1. Создайте нового бота через [@BotFather](https://t.me/botfather) и получите токен

2. Установите токен одним из способов:
   - Через переменную окружения:
     ```bash
     export TELEGRAM_BOT_TOKEN='your_token_here'
     ```
   - Или передайте токен при запуске:
     ```bash
     poetry run start-bot 'your_token_here'
     ```

## Использование

### Запуск бота

```bash
poetry run start-bot
```

### Команды бота

- `/start` - начало работы с ботом и список команд
- `/set_signature <текст>` - установить подпись
- `/remove_signature` - удалить подпись
- `/show_signature` - показать текущую подпись
- `/set_channel @channel_name` - установить канал для публикации
- `/remove_channel` - удалить канал
- `/show_channel` - показать текущий канал

### Примеры использования

1. Установка подписи:
```
/set_signature С уважением, Иван Иванов
CEO, Example Company
+7 (999) 123-45-67
```

2. Привязка канала:
```
/set_channel @my_channel
```

После настройки любое ваше сообщение будет автоматически дополняться подписью и публиковаться в указанном канале.

## Разработка

### Структура проекта

```
telegram-signature-bot/
├── pyproject.toml
├── README.md
├── telegram_signature_bot/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   └── bot.py
└── tests/
    ├── __init__.py
    ├── test_database.py
    └── test_bot.py
```

### Запуск тестов

```bash
poetry run pytest
```

### Линтинг и форматирование

```bash
poetry run black .
poetry run isort .
poetry run flake8
poetry run mypy .
```

## Требования

- Python 3.9+
- Poetry
- SQLite 3

## Лицензия

MIT License

## Поддержка

Если у вас возникли проблемы или есть предложения по улучшению бота, создайте Issue в репозитории проекта.

## Участие в разработке

1. Сделайте форк репозитория
2. Создайте новую ветку (`git checkout -b feature/improvement`)
3. Внесите изменения и сделайте коммит (`git commit -am 'Новая фича'`)
4. Отправьте изменения в ваш форк (`git push origin feature/improvement`)
5. Создайте Pull Request
