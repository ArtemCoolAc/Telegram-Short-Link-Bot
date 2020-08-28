import logging
from telegram.ext import Updater, CommandHandler
import requests
import validators
from local_settings import get_token, connect_to_database


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='log.txt')


class BotDatabase:
    class DatabaseConfig:
        connector = connect_to_database()

    def __init__(self):
        self.connection = self.DatabaseConfig.connector
        self.cursor = self.connection.cursor

    def _execute_command(self, command):
        self.cursor.execute(command)
        self.connection.commit()

    def create_history_table(self):
        command = f"CREATE TABLE IF NOT EXISTS request_history (" \
                  f"id SERIAL UNIQUE , "\
                  f"old_url VARCHAR(300), "\
                  f"new_url VARCHAR(30), "\
                  f"date TIMESTAMPTZ)"
        self._execute_command(command)

    def drop_history_table(self):
        command = f"DROP TABLE requests_history"
        self._execute_command(command)

    def insert_record(self, table_name, *args):
        command = f"""INSERT INTO {table_name} VALUES 
                  (DEFAULT, {"', '".join(args)});"""
        self._execute_command(command)

    def get_history_part(self, table_name='requests_history', quantity=10):
        command = f"""SELECT old_url, new_url, date from {table_name}
                  ORDER BY date DESC """
        self._execute_command(command)
        query_result = self.cursor.fetchall()
        return [ret for ret in query_result]


class Bot:
    class BotConfig:
        TOKEN = get_token()
        API_URL = 'https://rel.ink/api/links/'

    def __init__(self):
        updater = Updater(self.BotConfig.TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        start_handler = CommandHandler('start', Bot.start)
        url_handler = CommandHandler('shorten', Bot.short_link, pass_args=True)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(url_handler)
        updater.start_polling()
        self.database = BotDatabase()

    @staticmethod
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I'm a bot and I'm able to do 2 things: \
                                     1) I can shorten your link via https://rel.ink/; \
                                     2) Return the history of 10 last links you wrote me")

    def short_link(self, update, context):
        logging.info(context.args)
        url = context.args[0]
        if len(context.args) > 1 or not validators.url(context.args[0]):
            context.bot.send_message(chat_id=update.effective_chat.id, text='Некорректный URL')
        session = requests.Session()
        request_data = {'url': url}
        response = session.post(Bot.BotConfig.API_URL, request_data)
        response_data = response.json()
        hashid, old_url, creation_time = response_data['hashid'], request_data['url'], response_data['created_at']
        logging.info(f'{hashid}, {old_url}, {creation_time}')
        short_url = f'https://rel.ink/{hashid}'
        message = f'Сокращенная ссылка {short_url}'
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        session.close()
        self.database.insert_record(old_url, short_url, creation_time)


if __name__ == '__main__':
    A = Bot()
