# -*- coding: utf-8 -*-

import telebot, requests
import json
from telebot.types import Message
from pymongo import MongoClient

token = '1234527124:AAHUVJO08IFAzAYlFHcikdSAhEtKAKhq3As'
bot = telebot.TeleBot(token)
backurl = 'http://localhost:5000'

client = MongoClient('localhost', 27017)
db = client.subscribed_usersDB


@bot.message_handler(commands=['start'])
def init(message):
    print(message.from_user)
    chat_id = message.from_user.id

    welcome_mesage = '''
Привет! Это официальный бот сервиса объявлений KBTUBoard!
Вот список доступных команд:
/validate *код* - для подтверждения кода для регистрации на сайте 
/subscribe - подписаться на обновления "Потеряно и найдено"
/unsubscribe - отписаться от обновлений "Потеряно и найдено" 
    '''
    bot.send_message(chat_id, welcome_mesage)


@bot.message_handler(commands=['validate'])
def validate_code(message):
    chat_id = message.from_user.id
    username = message.from_user.username
    try:
        code = message.text.split(' ')[1]

        if username == None:
            bot.send_message(chat_id,
                             'У вас не присвоено имя пользователя Telegram. Сделайте это в настройках профиля и попробуйте еще раз.')
            return False

        bot.send_message(chat_id, 'Подтверждаем код...')
        try:
            r = requests.post(url=f'{backurl}/code',
                              headers={'content-type': 'application/json'},
                              json=({
                                  'code': code,
                                  'chat_id': chat_id,
                                  'telegram_username': username
                              }),
                              )

            data = r.text

            print(data)
            if r.status_code == 200:
                bot.send_message(chat_id, 'Код был успешно подтвержден!')
            elif r.status_code == 201:
                bot.send_message(chat_id, 'Код уже был подтвержден.')
            elif r.status_code == 404:
                bot.send_message(chat_id, 'Данный код не был найден. Проверьте его и попробуйте еще раз.')
            else:
                bot.send_message(chat_id, 'Произошла неизвестная ошибка. Попробуйте еще раз.')
        except Exception as e:
            bot.send_message(chat_id, 'Произошла неизвестная ошибка. Попробуйте еще раз.')
            print(str(e))
    except:
        bot.send_message(chat_id, 'Код былл введен неправильно!')


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    chat_id = message.from_user.id

    users = db.subscribed_users

    if users.find({'_id': chat_id}).count() > 0:
        if users.find({'_id': chat_id})[0].get('subscribed') == False:
            users.update_one({'_id': chat_id}, {'$set': {'subscribed': True}})
            bot.send_message(chat_id,
                             'Вы были успешно подписаны на обновления "Потеряно и найдено"! Для отмены подписки используйте команду /unsubscribe.')
        else:
            bot.send_message(chat_id,
                             'Вы уже подписаны на обновления "Потеряно и найдено"! Для отмены подписки используйте команду /unsubscribe.')

    else:
        user = users.insert_one({
            '_id': chat_id,
            'subscribed': True,
        })
        bot.send_message(chat_id,
                         'Вы были успешно подписаны на обновления "Потеряно и найдено"! Для отмены подписки используйте команду /unsubscribe.')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    chat_id = message.from_user.id

    users = db.subscribed_users
    if users.find({'_id': chat_id}).count() > 0:
        users.update_one({'_id': chat_id}, {'$set': {'subscribed': False}})
        bot.send_message(chat_id, 'Вы отписаны от обновлений "Потеряно и найдено".')
    else:
        bot.send_message(chat_id,
                         'Вы не подписаны на обновления "Потеряно и найдено". Чтобы подписаться используйте команду /subscribe.')


if __name__ == '__main__':
    try:
        print('Starting the bot...')
        bot.polling()
    except Exception as e:
        print(str(e))
