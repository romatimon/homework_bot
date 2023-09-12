import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправляем сообщение в Телеграмм чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Ошибка отправки сообщения: {error}')
        raise Exception
    else:
        logger.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Делаем запрос к API."""
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params=timestamp)
    except requests.RequestException:
        raise Exception('Ошибка при запросе к API сервису')
    if response.status_code != HTTPStatus.OK:
        logger.error(f'Эндпоин {ENDPOINT} недоступен')
        raise Exception(f'Ответ API: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверяем ответ от API."""
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарем')
    if 'homeworks' not in response:
        raise KeyError('Ответ не содержит ключ homeworks')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Ключ homeworks не является списком')
    return response['homeworks']


def parse_status(homework):
    """Получаем статус домашей работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        raise KeyError('Отсутсвует ключ homework_name')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError('Необходимый статус отсутствует')
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует обязательная переменная окружения.')
        raise Exception

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    timestamp = {'from_date': current_timestamp}

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            current_timestamp = response.get(
                'current_date',
                int(time.time()) - RETRY_PERIOD
            )
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
