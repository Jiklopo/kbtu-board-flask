import datetime

import pymongo
from bson import ObjectId
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug import exceptions

import tools.password_manager as pm
import tools.tools as t
from database.posts import PostCollection
from database.users import UserCollection

app = Flask(__name__)
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['kbtu_board']
userdb = UserCollection(db)
postdb = PostCollection(db)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'lol_kek_cheburek'


@app.route('/login', methods=['POST'])
def obtain_token():
    data = get_data(request)
    try:
        username = data['username']
        password = data['password']
    except:
        raise exceptions.BadRequest

    user = userdb.users.find_one(dict(username=username))
    if user is None:
        raise exceptions.NotFound

    password_manager = pm.PasswordManager(user.get('password'))

    if password_manager.verify_password(password):
        token = create_access_token(identity=dict(id=str(user.get('_id')),
                                                  username=username,
                                                  telegram_username=user.get('telegram_username')),
                                    expires_delta=datetime.timedelta(minutes=30))
        return jsonify(dict(token=token))
    raise exceptions.BadRequest


@app.route('/users', methods=['GET'])
def users():
    return userdb.get_users(get_data(request))


@app.route('/user', methods=['POST'])
def get_post_user():
    data = get_data(request)
    data['password'] = pm.PasswordManager.hash_password(data['password'])
    return userdb.create_user(**data)


@app.route('/user', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def put_delete_user():
    data = get_data(request)
    if request.method == 'DELETE':
        return userdb.delete_user(get_id())
    elif request.method == 'PUT':
        return userdb.update_user(get_id(), data)
    elif request.method == 'GET':
        return userdb.get_user(get_id())


@app.route('/code', methods=['GET', 'POST'])
def code():
    if request.method == 'GET':
        return userdb.generate_code()
    elif request.method == 'POST':
        return userdb.validate_code(request.get_json())


@app.route('/check-code', methods=['GET'])
def check_code():
    return userdb.check_code(get_data(request).get('code'))


@app.route('/teacher', methods=['PUT', 'POST', 'DELETE'])
@jwt_required
def teacher():
    data = get_data(request)
    if request.method == 'DELETE':
        return userdb.unregister_teacher(get_id())
    if request.method == 'POST':
        return userdb.register_teacher(get_id(), **data)
    return userdb.update_teacher(get_id(), data)


@app.route('/teacher/like', methods=['PUT'])
def like_teacher():
    id = get_data(request).get('teacher_id')
    if not id:
        raise exceptions.BadRequest
    return userdb.rate_teacher(id, 1)


@app.route('/teacher/dislike', methods=['PUT'])
def dislike_teacher():
    id = get_data(request).get('teacher_id')
    if not id:
        raise exceptions.BadRequest
    return userdb.rate_teacher(id, -1)


@app.route('/search/study', methods=['GET'])
def get_teachers():
    data = get_data(request)
    return userdb.get_teachers(data)


@app.route('/search/lost', methods=['GET'])
def get_posts():
    data = get_data(request)
    return postdb.get_posts(**data)


@app.route('/lost', methods=['POST'])
@jwt_required
def create_post():
    data = get_data(request)
    data['user_id'] = ObjectId(get_id())
    data['telegram_username'] = get_jwt_identity()['telegram_username']
    return postdb.create_post(**data)


@app.route('/lost/<id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def post(id):
    data = get_data(request)
    p = postdb.posts.find_one(t.id_query(id))
    if not p:
        raise exceptions.NotFound
    if p.get('user_id') != get_id():
        raise exceptions.Forbidden
    if request.method == 'GET':
        return postdb.get_post(**data)
    elif request.method == 'PUT':
        return postdb.update_post(t.id_query(id), data)
    elif request.method == 'DELETE':
        return postdb.delete_post(**t.id_query(id))


@app.route('/test', methods=['GET'])
@jwt_required
def test():
    return get_jwt_identity()


@app.errorhandler(400)
def error_400(e):
    return jsonify(dict(error=str(e)), status=400)


@app.errorhandler(403)
def error_403(e):
    return jsonify(dict(error='This is a secret you will never know.'))


@app.errorhandler(404)
def error_404(e):
    return jsonify(dict(error='This page does not exist.'))


@app.errorhandler(405)
def error_405(e):
    return jsonify(dict(error='There is no such method available for this page.'))


@app.errorhandler(500)
def error_500(e):
    return jsonify(dict(error='Krivorukiy programmist.'))


def get_data(request):
    data = request.get_json()
    if data is None:
        data = {}
    elif data.get('id'):
        data['_id'] = ObjectId(data['id'])
    return data


def get_id():
    return ObjectId(get_jwt_identity()['id'])
