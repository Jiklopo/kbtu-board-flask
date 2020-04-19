import pymongo
from .tools import jsonify
from flask import jsonify as jsonify_original

class PostCollection:
    col: pymongo.collection.Collection

    def __init__(self, collection: pymongo.collection.Collection):
        self.col = collection

    def get_posts(self, **filter):
        return jsonify_original(
            [dict(post) for post in self.col.find(filter)]
        )

    def get_post(self, **filter):
        pass

    def create_post(self, **data):
        pass

    def update_post(self, filter: dict, update: dict):
        pass

    def delete_post(self, **filter):
        pass
