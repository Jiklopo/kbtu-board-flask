import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['test']
col = (db['test'])

doc = col.insert_one({'test': 'test'})
print(col.find_one({'test': 'test'}))
