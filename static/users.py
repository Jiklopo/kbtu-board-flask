import pymongo
from .tools import jsonify
from flask import Response
from flask import jsonify as jsonify_orig

'''
User Fields:

username
password(hash)
name
telegram_chat_id:
telegram_login:
'''


class UserCollection:
    col: pymongo.collection.Collection

    def __init__(self, collection: pymongo.collection):
        self.col = collection

    def get_users(self, limit=10):
        return jsonify_orig([dict(u) for u in self.col.find({}, {'_id': 0})[:limit]])

    def get_user(self, **params):
        user = self.col.find_one(params)
        if user is None:
            return jsonify(dict(error='No such user exists'))
        return jsonify(user)

    def add_user(self, user: dict):
        if self.validate_user(user):
            u = self.col.insert_one(user).inserted_id
            return Response(jsonify({'_id': u}), status=201)
        return Response(jsonify(dict(error='Invalid input')), status=204)

    def delete_user(self, **params):
        u = self.col.delete_one(params)
        if u.acknowledged:
            return Response(status=200)
        return jsonify(dict(error='No such user exists.'))

    def update_user(self, filter, update):
        u = self.col.update_one(filter, {'$set': update})
        print(u)
        return 'asfd'

    @staticmethod
    def validate_user(user: dict):
        keys = user.keys()
        if len(keys) > 5:
            return False
        for i in ['username', 'password', 'telegram_chat_id', 'telegram_username']:
            if i not in keys:
                return False
        return True
