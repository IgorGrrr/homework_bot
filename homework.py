import os
import sys
import time
import telegram
import logging
import requests
import exceptions
import settings
from http import HTTPStatus



from dotenv import load_dotenv



load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='homework_bot.log',
    filemode='a',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# RETRY_TIME = 600
# ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
# HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


# HOMEWORK_STATUSES = {
#     'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
#     'reviewing': 'Работа взята на проверку ревьюером.',
#     'rejected': 'Работа проверена: у ревьюера есть замечания.'
# }


def send_message(bot, message):
    """Отправка сообщения в telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Сообщение отправлено')
    except Exception as e:
        logger.error(f'Не получилось отправить сообщение: {e}')


def get_api_answer(current_timestamp):
    """Получение ответа на запрос к API-сервису"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            settings.ENDPOINT,
            headers=settings.HEADERS,
            params=params
        )
    except Exception as e:
        logging.error(f'Произошла ошибка: {e}')
    if response.status_code != HTTPStatus.OK:
        message = (f'Запрос к эндпоинту вернул код {HTTPStatus.code}')
        raise requests.exceptions.RequestException(message)
    #try:
    return response.json()
    # except ValueError:
    #     logger.error('Ответ получен не в формате json')
    #     return {}


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        message = 'Неправильный тип полученного ответа'
        logging.error(message)
        raise TypeError(message)
    if response.get('homeworks') is None:
        message = 'В полученном ответе отсутсвует необходимый ключ homeworks'
        logging.error(message)
        raise exceptions.MissingHomeworkKey(message)
    if not isinstance(response['homeworks'], list):
        message = 'Перечень домашних работ должен содержаться в списке'
        logging.error(message)
        raise exceptions.HomeworksNotInList(message)
    return response.get('homeworks')

def parse_status(homework):
    """Получение статуса домашней работы."""
    if not (('homework_name' in homework) and ('homework_status' in homework)):
        logging.error('Отсутствуют имя или статус домашней работы')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = settings.HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех необходимых переменных окружения."""
    envvars = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    for envvar in envvars:
        if envvar is None:
            logger.critical(f'Отстутствует переменная окружения: {envvar}')
            return  False
    return True

def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                send_message(bot ,parse_status(homeworks[0]))
            else:
                logger.debug('Статус работы не изменился')
            current_timestamp = current_timestamp
            time.sleep(settings.RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(settings.RETRY_TIME)
        else:
            time.sleep(settings.RETRY_TIME)


if __name__ == '__main__':
    main()
