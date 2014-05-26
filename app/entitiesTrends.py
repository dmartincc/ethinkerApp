from datetime import datetime, timedelta

period = datetime.now() - timedelta(hours=6)

def get_db(db_name):
    from pymongo import MongoClient
    uri = 'mongodb://user:passw0rd@oceanic.mongohq.com:10024/dev-ethinker'
    client = MongoClient(uri)
    db = client[db_name]
    return db  

def getTrends():
    db = get_db('dev-ethinker')    
    pipeTopMentions = [{"$match":{ "date":{"$gt": period}}},
                                {"$unwind":"$entities"},
                                {"$group":{"_id":"$entities", "count":{"$sum":1}}},
                                {"$sort":{"count":-1}}]    

    mongoData = db.articles.aggregate(pipeTopMentions)
    entities=[]
    for item in mongoData['result'][0:9]:
        dic={}
        dic['entity']=item['_id']
        dic['num']=item['count']        
        entities.append(dic)    
    return entities

def getEntities():
    db = get_db('dev-ethinker')    
    pipeTopMentions = [{"$match":{ "date":{"$gt": period}}},
                                {"$unwind":"$entities"},
                                {"$group":{"_id":"null", "count":{"$sum":1}}}]    

    mongoData = db.articles.aggregate(pipeTopMentions)        
    return mongoData['result'][0]['count']

        

def getCategories():
    db = get_db('dev-ethinker')
    pipeTopCategories = [{"$match":{ "date":{"$gt": period}}},
                       {"$unwind":"$tags"},
                       {"$group":{"_id":"$tags", "count":{"$sum":1}}},
                       {"$sort":{"count":-1}}]

    mongoDataCat = db.articles.aggregate(pipeTopCategories)
    categories=[]
    for item in mongoDataCat['result'][0:9]:
        dic={}
        dic['category']=item['_id']
        dic['num']=item['count']        
        categories.append(dic)    
    return categories


def main():
    dic={}
    db = get_db('dev-ethinker')
    dic['totalArticles'] = db.articles.find().count()
    dic['articles'] = db.articles.find({"date":{"$gt": period}}).count()
    dic['sources'] = db.sources.find().count()
    dic['categories'] = getCategories()
    dic['entities'] = getTrends()
    dic['numEntities'] = getEntities()
    dic['date']= datetime.utcnow()
    db.trends.insert(dic)


if __name__ == '__main__':
    main()