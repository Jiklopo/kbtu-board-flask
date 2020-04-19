from bson import ObjectId
from flask import Flask, request, jsonify, Response
import pymongo
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from database.users import UserCollection
from database.posts import PostCollection
from werkzeug import exceptions

app = Flask(__name__)
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['kbtuBoard']
userdb = UserCollection(db['users'])
postdb = PostCollection(db['posts'])
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

    if user.get('password') == password:
        token = create_access_token(identity=dict(id=str(user.get('_id')), username=username))
        return jsonify(dict(token=token))
    raise exceptions.BadRequest


@app.route('/users', methods=['GET'])
def users():
    return userdb.get_users()


@app.route('/user', methods=['GET', 'POST'])
def get_post_user():
    data = get_data(request)
    if request.method == 'GET':
        return userdb.get_user(**data)
    elif request.method == 'POST':
        return userdb.create_user(data)
    raise exceptions.MethodNotAllowed


@app.route('/api/user', methods=['PUT', 'DELETE'])
@jwt_required
def put_delete_user():
    data = get_data(request)
    if request.method == 'DELETE':
        return userdb.delete_user(**{'_id': get_id()})
    elif request.method == 'PUT':
        return userdb.update_user({'_id': get_id()}, data)
    raise exceptions.MethodNotAllowed


@app.route('/teacher', methods=['PUT, POST'])
@jwt_required
def teacher():
    data = get_data(request)
    return userdb.register_teacher(get_jwt_identity()['id'], **data)


@app.route('/lost', methods=['GET'])
def get_posts():
    data = get_data(request)
    return postdb.get_posts(**data)


@app.route('/lost', methods=['POST'])
@jwt_required
def create_post():
    data = get_data(request)
    return postdb.create_post(**data)


@app.route('/lost>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def post():
    data = get_data(request)
    if request.method == 'GET':
        return postdb.get_post(**data)
    elif request.method == 'POST':
        return postdb.create_post()
    elif request.method == 'PUT':
        return postdb.update_post(data.get('filter'), data.get('update'))
    elif request.method == 'DELETE':
        return postdb.delete_post(**data)
    raise exceptions.BadRequest


@app.route('/test')
@jwt_required
def test():
    return get_jwt_identity()


@app.errorhandler(400)
def error_400(e):
    return jsonify(dict(error=str(e)))


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
    return data


def get_id():
    return ObjectId(get_jwt_identity()['id'])


if __name__ == '__main__':
    app.run()
