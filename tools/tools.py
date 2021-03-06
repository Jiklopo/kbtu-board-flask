try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError
import datetime
from bson.objectid import ObjectId
from werkzeug import Response


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def jsonify(object):
    return Response(json.dumps(dictify(object)), mimetype='application/json')


def dictify(mongo_object):
    d = dict(mongo_object)
    if d.get('_id'):
        d['_id'] = str(d['_id'])
        d['id'] = d['_id']
    if d.get('user_id'):
        d['user_id'] = str(d['user_id'])
    return d


def id_query(id):
    return {'_id': ObjectId(id)}


def get_error(message: str, code=500):
    return Response(dict(error=message), status=code, content_type='application/json')
