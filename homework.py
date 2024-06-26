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


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def send_message(bot, message):
    """Отправляем сообщение в Телеграмм чат."""
    try:
        logging.debug('Бот отправил сообщение в Телеграмм чат.')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise Exception(f'Ошибка отправки сообщения: {error}')
    else:
        logging.info('Сообщение отправлено')


def get_api_answer(timestamp):
    """Делаем запрос к API."""
    try:
        logging.debug('Бот делает запрос к API домашней работы')
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params=timestamp)
    except requests.RequestException:
        raise Exception(f'Ошибка при запросе к API сервису: {ENDPOINT}')
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Ответ API: {response.status_code}')
    return response.json()


def check_response(response):
    """Проверяем ответ от API."""
    logging.debug('Проверяем ответ API на соответствие документации')
    if not isinstance(response, dict):
        raise TypeError(f'Ответ получен ввиде {type(response)},'
                        f'а ожидается словарь {dict}')
    if 'homeworks' not in response:
        raise KeyError('Ответ не содержит ключ homeworks')
    if not isinstance(response['homeworks'], list):
        raise TypeError(f'Ответ под ключем homeworks получен'
                        f'ввиде {type(response["homeworks"])},'
                        f'а ожидается список: {list}')
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
        logging.critical('Отсутствует обязательная переменная окружения.')
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
            else:
                logging.debug('Новые статусы домашней работы отсутствуют')
            current_timestamp = response.get(
                'current_date',
                int(time.time()) - RETRY_PERIOD
            )
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error({message})
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    main()
