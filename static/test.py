from app import db
col = db['users']


def to_dict(user):
    return dict(
        username=user['username'],
        password=user['password'],
        name=user['name'],
        telegram_chat_id=user['telegram_chat_id'],
        telegram_username=user['telegram_username']
    )


print(dict(col.find_one({}, {'_id': 0})))





