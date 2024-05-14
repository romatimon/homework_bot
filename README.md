## Бот для проверки статуса домашней работы.

## 
- для создания и работы бота (Bot API) использовал библиотеку python-telegram-bot;
- реализовал логику обработки команд и отправки соответствующих запросов к API, а также последующего ответа от API и направлению информации о статусе домашней работы через Telegram;
- настроил логиронивае событий;
- для работы 24\7 разместил бота на удаленном сервере (pythonanywhere).

## Используемые технологии:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7


### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/romatimon/homework_bot
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

Запустить проект:

```
python homework.py
```

Автор [romatimon](https://github.com/romatimon)
