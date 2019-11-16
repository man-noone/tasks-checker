import os
import logging

from telegram.ext import Updater
from telegram.ext import CommandHandler


TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
G = {}

from config import logger
from devman import DevmanAPI

class BotHandler(logging.Handler):
    def __init__(self, bot):
        logging.Handler.__init__(self)
        self.bot = bot

    def emit(self, record):
        print()
        print('----------')
        print(G.get('chat_id'))
        print('----------')
        print()
        msg = self.format(record)
        self.bot.send_message(chat_id=G.get('chat_id'), text=msg)


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
    # chat_id = update.effective_chat.id
    logger.debug(f'Update {update} caused error {context.error}')


def hello_user(update, context):
    username = update.effective_user.username
    message = f'Hello, {username}!'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def check(update, context):
    G['chat_id'] = update.effective_chat.id

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
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    bot = updater.bot

    start_handler = CommandHandler('start', hello_user)
    dispatcher.add_handler(start_handler)

    check_handler = CommandHandler('check', check)
    dispatcher.add_handler(check_handler)

    dispatcher.add_error_handler(error)

    bot_handler = BotHandler(bot)
    bot_handler.setLevel(logging.DEBUG)
    logger.addHandler(bot_handler)

    # from devman import DevmanAPI

    updater.start_polling()
    updater.idle()
