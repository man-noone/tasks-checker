import os
import logging
from contextvars import ContextVar

import requests
from telegram.ext import Updater
from telegram.ext import CommandHandler

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
DEVMAN_TOKEN=os.environ['DEVMAN_TOKEN']

logger = logging.getLogger('bot_logger')
chat_id = ContextVar('chat_id')



class BotHandler(logging.Handler):
    def __init__(self, bot):
        logging.Handler.__init__(self)
        self.bot = bot

    def emit(self, record):
        msg = self.format(record)
        self.bot.send_message(chat_id=chat_id.get(), text=msg)


class DevmanAPI:
    def __init__(self, url='https://dvmn.org/api/user_reviews/', timeout=None):
        self._url = url
        self._timeout = timeout
        self._params = {}

        self.response = self._make_request(url=self._url, params=self._params, timeout=self._timeout)


    def _make_request(self, url='', params=None, timeout=None):

        headers = {'Authorization': f'token {DEVMAN_TOKEN}'}

        while True:
            try:
                r = requests.get(url, headers=headers,
                                      params=params,
                                      timeout=timeout)
                r.raise_for_status()

            except requests.exceptions.ReadTimeout:
                logger.debug('Timeout', exc_info=True)
                continue
            except requests.exceptions.ConnectionError:
                logger.debug('Connection Error', exc_info=True)
                continue
            else:
                response = r.json()
                status = response.get('status')

                logger.debug(f'Got from server: {response}')

                if status == 'timeout':
                    params.update({'timestamp': response.get('timestamp_to_request')})
                    logger.debug(f"Server's timeout is running out. {response}")
                    continue
                elif status == 'found':
                    logger.debug(f'Server found submitted works - {response}')
                    return response
                else:
                    return None

    def __str__(self):
        return f'<DevmanAPI. Result: {self.response}>'


def fetch_updates():
    try:
        devman_obj = DevmanAPI(url='https://dvmn.org/api/long_polling/', timeout=100)
    except Exception as e:
        logger.debug(f'Exception: {e}', exc_info=True)
        devman_obj = None

    if not devman_obj:
        return None

    response = devman_obj.response
    last_attempt = response.get('new_attempts')[-1]

    is_negative = last_attempt.get('is_negative', '')
    lesson_title = last_attempt.get('lesson_title', '')
    lesson_url = 'https://dvmn.org' + last_attempt.get('lesson_url', '')

    result = {
              'is_negative': is_negative,
              'lesson_title': lesson_title,
              'lesson_url': lesson_url
    }

    return result


def error(update, context):
    chat_id.set(update.effective_chat.id)
    logger.debug(f'Update {update} caused error {context.error}')


def hello_user(update, context):
    chat_id.set(update.effective_chat.id)

    username = update.effective_user.username
    message = f'Hello, {username}!'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def check(update, context):
    chat_id.set(update.effective_chat.id)

    logger.info('Стартую... пщщщ... пип-пип!')
    result = fetch_updates()

    if not result:
        message = 'Ошибка 404, либо неверны параметры запроса.'
    else:
        if result.get('is_negative'):
            status = 'Не принято'
        else:
            status = 'Принято'

        lesson_title = result.get('lesson_title')
        lesson_url = result.get('lesson_url')

        message = f'Статус: {status}\nРабота: {lesson_title}\nСсылка: {lesson_url}'

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d.%b.%Y %H:%M:%S')

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    bot = updater.bot

    bot_handler = BotHandler(bot)
    bot_handler.setLevel(logging.DEBUG)
    logger.addHandler(bot_handler)

    start_handler = CommandHandler('start', hello_user)
    dispatcher.add_handler(start_handler)

    check_handler = CommandHandler('check', check)
    dispatcher.add_handler(check_handler)

    dispatcher.add_error_handler(error)

    while True:
        try:
            updater.start_polling()
            updater.idle()
        except Exception as e:
            logger.debug(f'Error occured:\n{e}', exc_info=True)
