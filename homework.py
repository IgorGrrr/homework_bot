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

HEADERS = {'Authorization': f'OAuth {os.getenv("PRACTICUM_TOKEN")}'}

load_dotenv()

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_message(bot, message):
    """Отправка сообщения в telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        message = 'Не получилось отправить сообщение'
        logger.error(message)
    else:
        logger.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Получение ответа на запрос к API-сервису."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            settings.ENDPOINT,
            headers=HEADERS,
            params=params
        )
        logger.info('Начинаем запрос к API')
    except exceptions.APIRequestError:
        message = 'При запросе к API произошла ошибка'
        logging.error(message)
    if response.status_code != HTTPStatus.OK:
        message = (f'Запрос к эндпоинту вернул код {HTTPStatus.code}')
        raise exceptions.WrongHTTPStatus(message)
    return response.json()


def check_response(response):
    """Проверка ответа API на корректность."""
    homeworks = response['homeworks']
    if not isinstance(response, dict):
        message = 'Неправильный тип полученного ответа'
        raise TypeError(message)
    if homeworks  is None:
        message = 'В полученном ответе отсутсвует ключ homeworks'
        raise exceptions.MissingHomeworkKey(message)
    elif response.get('current_date') is None:
        message = 'В полученном ответе отсутсвует ключ current_date'
        raise exceptions.MissingHomeworkKey(message)
    if not isinstance(homeworks, list):
        message = 'Перечень домашних работ должен содержаться в списке'
        raise exceptions.HomeworksNotInList(message)
    return homeworks


def parse_status(homework):
    """Получение статуса домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if not (('homework_name' in homework) and ('status' in homework)):
        message = 'Отсутствуют имя или статус домашней работы'
        raise exceptions.MissingHwrkNameOrStatus(message)
    if homework_status not in settings.HOMEWORK_STATUSES:
        message = 'Статус домашней работы отличается от ожидаемого'
        raise KeyError(message)
    verdict = settings.HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия всех необходимых переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        level=logging.DEBUG,
        filename='homework_bot.log',
        filemode='a',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)
    if not check_tokens():
        message = 'Отстутствует переменная окружения'
        logger.critical(message)
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                send_message(bot, parse_status(homeworks[0]))
            else:
                logger.debug('Статус работы не изменился')
            current_timestamp = response['current_date']

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        finally:
            time.sleep(settings.RETRY_TIME)


if __name__ == '__main__':
    main()
