# Бот КиноПоиска

### Чтобы запустить бота нужно:

Создать бота в телеграмме с помощью BotFather и получить токен.

Получить токен для API киноПоиска на сайте https://kinopoisk.dev

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:vir2ozz2009/kinopoisk_bot.git
```

Cоздать и активировать виртуальное окружение:

Для Mac:
```
python3 -m venv venv
```

Для Windows:
```
python -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

В главной директории создать файл ".env" и поместить в него токены:

```
TELEGRAM_TOKEN = your_token
KINOPOISK_TOKEN2 = 'your token'
```

Запустить файл Kinopisk_API_bot_v_3.py
