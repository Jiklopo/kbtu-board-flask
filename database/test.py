import pymongo, string, random


def gen_code(length=5):
    chars = string.ascii_lowercase + string.digits + string.ascii_uppercase
    code = ''.join(random.choices(chars, k=length))
    return code

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['test']
col = (db['test'])

doc = col.insert_one({'test': 'test'})
print(col.find_one({'test': 'test'}))
for i in range(5):
    print(gen_code())

a = dict(lol='kek')
b = dict(lol=a['lol'])
del a['lol']
print(b)
