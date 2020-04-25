# -*- coding: utf-8 -*-

import json
import pika
import telebot
from pymongo import MongoClient

TELEGRAM_TOKEN = '1234527124:AAHUVJO08IFAzAYlFHcikdSAhEtKAKhq3As'
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = MongoClient('localhost', 27017)
db = client['subscribed_usersDB']


class MetaClass(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        """ Singelton Design Pattern  """

        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class RabbitMqServerConfigure(metaclass=MetaClass):

    def __init__(self, host='localhost', queue='posts'):
        # """ Server initialization   """

        self.host = host
        self.queue = queue


class rabbitmqServer():

    def __init__(self, server):
        self.server = server
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server.host))
        self._channel = self._connection.channel()
        self._tem = self._channel.queue_declare(queue=self.server.queue)
        print("Server started waiting for Messages ")

    @staticmethod
    def callback(ch, method, properties, body):
        post = json.loads(body)
        users = db['subscribed_users'].find({'subscribed': True})
        print(users)
        for user in users:
            bot.send_message(user.get('_id'),
                             '''
                 Новое объявление!
                 
                 Заголовок:
                 %s
                 
                 Описание:
                 %s
                 
                 От:
                 @%s
                 
                 
                 Вы видите это сообщение потому, что подписались на обновления "Потеряно и найдено".
                 Для отмены подписки используйте команду /unsubscribe.
                 
                             ''' % (post.get('title'), post.get('description'), post.get('telegram_username')))

    def startserver(self):
        self._channel.basic_consume(
            queue=self.server.queue,
            on_message_callback=rabbitmqServer.callback,
            auto_ack=True)
        self._channel.start_consuming()


if __name__ == "__main__":
    serverconfigure = RabbitMqServerConfigure(host='localhost',
                                              queue='posts')


    server = rabbitmqServer(server=serverconfigure)
    server.startserver()
