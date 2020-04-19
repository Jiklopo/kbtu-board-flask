import pymongo
from bson import ObjectId

from .tools import jsonify, dictify
from flask import Response
from flask import jsonify as jsonify_orig
from werkzeug import exceptions

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

    def __init__(self, users: pymongo.collection.Collection):
        self.users = users

    def get_users(self, query, limit=10):
        return jsonify_orig([dictify(u) for u in self.users.find(query, {'password': 0})[:limit]])

    def get_user(self, **params):
        user = self.users.find_one(params)
        if user is None:
            return jsonify(dict(error='No such user exists'))
        return jsonify_orig(dictify(user))

    def get_user_by_id(self, id):
        user = self.users.find_one({'_id': ObjectId(id)})
        if user is None:
            return jsonify(dict(error='No such user exists'))
        return jsonify(user)

    def create_user(self, user: dict):
        if self.validate_user(user):
            u = self.users.insert_one(user).inserted_id
            return Response(jsonify({'_id': u}), status=201)
        raise exceptions.BadRequest

    def delete_user(self, id):
        u = self.users.delete_one({'_id': ObjectId(id)})
        if u.deleted_count > 0:
            return Response(status=200)
        return jsonify(dict(error='No such user exists.'))

    def update_user(self, query, update):
        u = self.users.update_one(query, {'$set': update})
        if u.matched_count == 0:
            raise exceptions.NotFound
        return Response(status=204)

    def unregister_teacher(self, id):
        return self.update_user({'_id': ObjectId(id)}, {'is_teaching': False})

    def register_teacher(self, id, **data):
        return self.update_user({'_id': ObjectId(id)}, {'teacher_info': data})

    def get_teachers(self, query):
        query['is_teaching'] = True
        return self.get_users(query)

    def generate_code(self):
        pass

    def check_code(self, code):
        pass

    def exists(self, username):
        return self.users.find({'username': username}) is None


    @staticmethod
    def validate_user(user: dict):
        keys = user.keys()
        if len(keys) > 5:
            return False
        for i in ['username', 'password', 'telegram_chat_id', 'telegram_username']:
            if i not in keys:
                return False
        return True
