# -*- coding: utf-8 -*

def get_db(db_name):
    from pymongo import MongoClient
    uri = 'mongodb://user:passw0rd@oceanic.mongohq.com:10024/dev-ethinker'
    client = MongoClient(uri)
    db = client[db_name]
    return db  


db = get_db('dev-ethinker')
status = db.articles.find()
for item in status:
	if "sentiment" in item:
		item["sentimentScore"]=item["sentiment"][0]
		item["sentimentCategory"]=item["sentiment"][1].encode('utf-8')
		db.articles.update({"titlePost":item['titlePost']},item)
		

