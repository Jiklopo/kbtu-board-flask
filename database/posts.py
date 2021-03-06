import json

import pymongo
from flask import Response
from flask import jsonify as jsonify_orig
from flask import jsonify as jsonify_original
from werkzeug import exceptions

from rabbit.publisher import RabbitPublisher
from tools.tools import dictify
from tools.tools import jsonify

'''
Post Fields:
    title
    description
    creation_date
    user_id
    time
    place
    photo

'''


class PostCollection:
    posts: pymongo.collection.Collection

    def __init__(self, database):
        self.posts = database['posts']
        self.publisher = RabbitPublisher()

    def get_posts(self, **filter):
        posts = self.posts.find(filter)
        return jsonify_original([dictify(post) for post in posts])

    def get_post(self, **params):
        post = self.posts.find_one(params)
        if post is None:
            return jsonify(dict(error='No such post exists'))
        return jsonify(post)

    def get_last_posts(self, limit=10):
        return jsonify_orig([dictify(p) for p in self.posts.find({}).sort({'time', -1})[:limit]])

    def create_post(self, **post):
        p = self.posts.insert_one(post).inserted_id
        message = {"title": post.get('title'),
                   "description": post.get('description'),
                   "telegram_username": post.get('telegram_username')}
        try:
            self.publisher.publish(json.dumps(message))
        except Exception as e:
            print(f'RabbitMQ exception: {str(e)}')
        return Response(str(p), status=201)

    def update_post(self, filter: dict, update: dict):
        p = self.posts.update_one(filter, {'$set': update})
        if p.matched_count == 0:
            raise exceptions.NotFound
        return Response(status=204)

    def delete_post(self, **params):
        p = self.posts.delete_one(params)
        if p.deleted_count > 0:
            return Response(status=200)
        return jsonify(dict(error='No such user exists.'))
