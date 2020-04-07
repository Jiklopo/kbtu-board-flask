from flask import Flask, request, Response
import pymongo
from static.users import UserDb

app = Flask(__name__)
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['kbtuBoard']
userdb = UserDb(db['users'])


@app.route('/api/users')
def users():
    return userdb.get_users()


@app.route('/api/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    if request.method == 'GET':
        data = request.get_json()
        return userdb.get_user(**data)
    elif request.method == 'POST':
        data = request.get_json()
        return userdb.add_user(data)
    elif request.method == 'DELETE':
        data = request.get_json()
        return userdb.delete_user(**data)
    elif request.method == 'PUT':
        data = request.get_json()
        return userdb.update_user(data)
    return 'chego?'


if __name__ == '__main__':
    app.run()
