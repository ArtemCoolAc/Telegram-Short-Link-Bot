import logging
from telegram.ext import Updater, CommandHandler
import requests
import validators
from local_settings import get_token, connect_to_database, get_private_data
from datetime import datetime
from collections import namedtuple
import psycopg2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG,
                    filename='log.txt')


class BotDatabase:
    class DatabaseConfig:

        @staticmethod
        def connect_to_bot_database():
            try:
                private = get_private_data()
                connection = psycopg2.connect(
                    user=private.user,
                    password=private.password,
                    host=private.host,
                    port=private.port,
                    database=private.database
                )
            except Exception as e:
                logging.error(e)
            return connection

    def __init__(self):
        self.connection = self.DatabaseConfig.connect_to_bot_database()
        self.cursor = self.connection.cursor()

    def _execute_command(self, command):
        try:
            self.cursor.execute(command)
            self.connection.commit()
        except Exception as exc:
            logging.error(exc)

    def create_history_table(self):
        command = f"CREATE TABLE IF NOT EXISTS request_history (" \
                  f"id SERIAL UNIQUE , " \
                  f"old_url VARCHAR(300), " \
                  f"new_url VARCHAR(30), " \
                  f"date TIMESTAMP)"
        self._execute_command(command)

    def drop_history_table(self):
        command = f"DROP TABLE requests_history"
        self._execute_command(command)

    def insert_record(self, *args):
        command = f"""INSERT INTO requests_history VALUES 
                  (DEFAULT, '{"', '".join(args)}');"""
        logging.info(command)
        self._execute_command(command)

    def get_history_part(self, quantity=10):
        command = f"""SELECT old_url, new_url, date FROM requests_history
                  ORDER BY date DESC LIMIT {quantity}"""
        logging.info(command)
        self._execute_command(command)
        query_result = self.cursor.fetchall()
        return [tuple(map(lambda x: x.strftime("%d %b %Y %H:%M:%S") if isinstance(x, datetime) else str(x), tup))
                for tup in query_result]


class Bot:
    class BotConfig:
        TOKEN = get_token()
        API_URL = 'https://rel.ink/api/links/'

    def __init__(self):
        try:
            self.database = BotDatabase()
            updater = Updater(self.BotConfig.TOKEN, use_context=True)
            dispatcher = updater.dispatcher
            start_handler = CommandHandler('start', self.start)
            url_handler = CommandHandler('shorten', self.short_link, pass_args=True)
            history_handler = CommandHandler('history', self.history, pass_args=True)
            dispatcher.add_handler(start_handler)
            dispatcher.add_handler(url_handler)
            dispatcher.add_handler(history_handler)
            updater.start_polling()
        except Exception as e:
            logging.error(e)

    @staticmethod
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot and I'm able to do 2 things: \
                                     1) I can shorten your link via https://rel.ink/ \
                                     2) Return the history of several (e.g. 10) last links you wrote me")

    def short_link(self, update, context):
        try:
            logging.info(f'Аргументы команды укорачивания: {context.args}')
            url = context.args[0]
            if len(context.args) > 1 or not validators.url(context.args[0]):
                context.bot.send_message(chat_id=update.effective_chat.id, text='Некорректный URL')
            else:
                with requests.Session() as session:
                    request_data = {'url': url}
                    response = session.post(Bot.BotConfig.API_URL, request_data)
                    if response.status_code == 201:
                        response_data = response.json()
                        hashid = response_data['hashid']
                        creation_time = str(datetime.now())
                        short_url = f'https://rel.ink/{hashid}'
                        message = f'Сокращенная ссылка {short_url}'
                        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                        self.database.insert_record(url, short_url, creation_time)
                    else:
                        message = 'Произошла ошибка во время запроса к API'
                        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        except Exception as e:
            logging.error(e)

    def history(self, update, context):
        try:
            quantity = 10
            if len(context.args) == 1 and context.args[0].isdecimal():
                quantity = context.args[0]
            query_result = self.database.get_history_part(quantity)
            bot_data = namedtuple('Query_data', ['user_link', 'short_link', 'date'])
            named_data = [bot_data(*tup) for tup in query_result]
            message = f'История последних успешных {quantity} обращений: \n' + \
                      '\n'.join([f'{idx + 1}) Обычная ссылка: {tup.user_link}, сокращенная: {tup.short_link},'
                                 f' время создания: {tup.date}' for idx, tup in enumerate(named_data)])
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)

        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    A = Bot()
