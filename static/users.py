import pymongo
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
    teachers: pymongo.collection.Collection

    def __init__(self, users: pymongo.collection.Collection, teachers: pymongo.collection.Collection):
        self.users = users
        self.teachers = teachers

    def get_users(self, limit=10):
        return jsonify_orig([dict(u) for u in self.users.find({}, {'_id': 0})[:limit]])

    def get_user(self, **params):
        user = self.users.find_one(params)
        if user is None:
            return jsonify(dict(error='No such user exists'))
        return jsonify(user)

    def add_user(self, user: dict):
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

    @staticmethod
    def validate_user(user: dict):
        keys = user.keys()
        if len(keys) > 5:
            return False
        for i in ['username', 'password', 'telegram_chat_id', 'telegram_username']:
            if i not in keys:
                return False
        return True
