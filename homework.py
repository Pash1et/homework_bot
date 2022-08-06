import logging
import os
import sys
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 60
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

FORMAT = '%(asctime)s - %(levelname)s : %(lineno)s : %(message)s'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler_stream = logging.StreamHandler()
handler = RotatingFileHandler(
    'main.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='utf-8',
)
handler.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(handler)
logger.addHandler(handler_stream)


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception:
        logger.error('Не удалось отправить сообщение в Telegram')
    else:
        logger.info('Сообщение успешно отправлено.')


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logger.error(f'Ошибка при запросе к API: {error}')
        raise Exception(f'Ошибка при запросе к API: {error}')
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        logger.error(f'Статус ошибки {status_code}')
        raise Exception(f'Статус ошибки {status_code}')
    return response.json()


def check_response(response: dict):
    """Проверка API на корректность."""
    try:
        homework = response['homeworks']
    except KeyError:
        logger.error('Отсутствует ключ homeworks')
        raise KeyError('Отсутствует ключ homeworks')
    try:
        homework = homework[0]
    except IndexError:
        logger.error('Список работ пуст')
        raise IndexError('Список работ пуст')
    return homework


def parse_status(homework):
    """Извлечение информации о последней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Нет ключа "homework_name"')
    if 'status' not in homework:
        raise KeyError('Нет ключа "status"')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    if (PRACTICUM_TOKEN is None or TELEGRAM_CHAT_ID is None
            or TELEGRAM_TOKEN is None):
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logger.critical(
            'Ошибка при получении глобальных переменных окружения. '
            'Программа принудительно остановлена.'
        )
        sys.exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    answer = {}

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            current_timestamp = response.get('current_date', current_timestamp)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if response.get('homeworks') != answer.get('homeworks'):
                send_message(bot, message)
                answer.update(response)
            time.sleep(RETRY_TIME)
        else:
            if response.get('homeworks') != answer.get('homeworks'):
                send_message(bot, message)
                answer.update(response)


if __name__ == '__main__':
    main()
