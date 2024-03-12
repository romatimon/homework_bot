## Homework Bot - Бот для проверки статуса домашней работы на код ревью в Яндекс.Практикум

# Используемые технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7


### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:PashkaVRN/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Записать в переменные окружения (файл .env) необходимые ключи:
- токен профиля на Яндекс.Практикуме
- токен телеграм-бота
- свой ID в телеграме


Запустить проект:

```
python homework.py
```
