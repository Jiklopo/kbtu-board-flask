import pymongo
from bson import ObjectId

from tools.tools import jsonify, dictify, id_query
from flask import Response
from flask import jsonify as jsonify_orig
from werkzeug import exceptions
import string
import random
import time

'''
User Fields:
    username
    password(hash)
    name
    telegram_chat_id
    telegram_username
    profile_photo
    faculty
    gender
    year_of_study

Teacher Field:
    subjects
    rating
    quote
'''


class UserCollection:
    users: pymongo.collection.Collection
    codes: pymongo.collection.Collection

    def __init__(self, database):
        self.users = database['users']
        self.codes = database['codes']

    def get_users(self, query, limit=10):
        return jsonify_orig([dictify(u) for u in self.users.find(query, {'password': 0})[:limit]])

    def get_user(self, user_id):
        user = self.users.find_one(id_query(user_id))
        if user is None:
            return jsonify(dict(error='No such user exists'))
        return jsonify_orig(dictify(user))

    def create_user(self, **data):
        if 'code' not in data:
            raise exceptions.BadRequest
        c = self.codes.find_one({'code': data['code']})
        if c is None or not c.get('is_valid'):
            raise exceptions.BadRequest
        self.codes.delete_one({'_id': c['_id']})
        for key in ['code', 'is_valid', '_id', 'creation_time']:
            del c[key]
        data['registration_time'] = time.time()
        data.update(c)
        u = self.users.insert_one(data).inserted_id
        return Response(jsonify({'_id': str(u)}), status=201)

    def delete_user(self, user_id):
        u = self.users.delete_one(id_query(user_id))
        if u.deleted_count > 0:
            return Response(status=200)
        return jsonify(dict(error='No such user exists.'))

    def update_user(self, user_id, update):
        u = self.users.update_one(id_query(user_id), {'$set': update})
        if u.matched_count == 0:
            raise exceptions.NotFound
        return Response(status=204)

    def unregister_teacher(self, user_id):
        return self.update_user(user_id, {'teacher_info.is_teaching': False})

    def register_teacher(self, user_id, **data):
        teacher_info = {'subjects': data.get('subjects'),
                        'rating': data['rating'] if 'rating' in data else 0,
                        'quote': data.get('quote'),
                        'is_teaching': data.get('is_teaching')
                        }
        keys = list(data.keys())[:]
        for i in keys:
            if i in ['subjects', 'rating', 'quote', 'is_teaching']:
                del data[i]
        data['teacher_info'] = teacher_info
        return self.update_user(user_id, data)

    def update_teacher(self, user_id, **data):
        user = self.users.find_one(id_query(user_id))
        if not user.get('teacher_info'):
            raise exceptions.BadRequest
        upd = {}
        for i in data.keys():
            upd[f'teacher_info.{i}'] = data[i]
        return self.update_user(user_id, upd)

    def get_teachers(self, query):
        query['teacher_info.is_teaching'] = True
        return self.get_users(query)

    def generate_code(self):
        code = self.gen_code()
        while self.codes.find({'code': code}).retrieved > 0:
            code = self.gen_code()
        self.codes.insert_one(dict(code=code, is_valid=False, creation_time=time.time()))
        return code

    def validate_code(self, data):
        # if not data.get('code') or not data.get('chat_id') or not data.get('telegram_username'):
        #     raise exceptions.BadRequest
        if self.codes.find_one({'code': data['code']})['is_valid']:
            return Response('Code already validated.', status=201)
        self.codes.update_one({'code': data['code']},
                              {'$set': {'is_valid': True,
                                        'chat_id': data['chat_id'],
                                        'telegram_username': data['telegram_username']}})
        return Response('Success', status=200)

    def check_code(self, code):
        c = self.codes.find_one(dict(code=code))
        if c is None:
            raise exceptions.NotFound
        if c and c.get('is_valid'):
            return Response('1')
        return Response('0')

    def exists(self, username):
        return self.users.find({'username': username}) is None

    @staticmethod
    def gen_code(length=5):
        chars = string.ascii_lowercase + string.digits + string.ascii_uppercase
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def validate_user(user: dict):
        keys = user.keys()
        if len(keys) > 5:
            return False
        for i in ['username', 'password']:
            if i not in keys:
                return False
        return True
