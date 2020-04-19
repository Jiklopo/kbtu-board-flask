import pymongo
from bson import ObjectId

from .tools import jsonify
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

    def get_users(self, limit=10):
        return jsonify_orig([u for u in self.users.find({}, {'_id': 0, 'password': 0})[:limit]])

    def get_user(self, **params):
        user = self.users.find_one(params)
        if user is None:
            return jsonify(dict(error='No such user exists'))
        return jsonify(user)

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

    def delete_user(self, **params):
        u = self.users.delete_one(params)
        if u.deleted_count > 0:
            return Response(status=200)
        return jsonify(dict(error='No such user exists.'))

    def update_user(self, filter, update):
        u = self.users.update_one(filter, {'$set': update})
        if u.matched_count == 0:
            raise exceptions.NotFound
        return Response(status=204)

    def register_teacher(self, id, **data):
        return self.update_user({'_id': ObjectId(id)}, data)

    def get_teacher(self, id):
        pass

    def exists(self, username):
        return self.users.find({'username': username}) is None

    @staticmethod
    def get_error(message: str, code=500):
        return Response(jsonify(dict(error=message), code))

    @staticmethod
    def validate_user(user: dict):
        keys = user.keys()
        if len(keys) > 5:
            return False
        for i in ['username', 'password', 'telegram_chat_id', 'telegram_username']:
            if i not in keys:
                return False
        return True
