# -*- coding: utf-8 -*-
from flask import render_template,request,redirect
from flask import jsonify
from app import app
import json, time, random, re, datetime
from datetime import datetime, timedelta
from random import randint

def treeHerarchy(data):
    name_to_node = {}
    root = {'name': 'Root', 'children': []}
    for parent, child in data:
        parent_node = name_to_node.get(parent)
        if not parent_node:
            name_to_node[parent] = parent_node = {'name': parent}
            root['children'].append(parent_node)
        name_to_node[child] = child_node = {'name': child}
        parent_node.setdefault('children', []).append(child_node)

    return root

def get_db(db_name):
    from pymongo import MongoClient
    uri = 'mongodb://user:passw0rd@oceanic.mongohq.com:10024/dev-ethinker'
    client = MongoClient(uri)
    db = client[db_name]
    return db  

def searchES(query):
    import pyes 
    conn = pyes.ES('http://dwalin-us-east-1.searchly.com/',
                basic_auth={'username': 'dev', 'password' : 'oqozmjudhxtbeagkjqzvj15tarseebyd'})
    q = pyes.StringQuery(query, default_operator="AND")
    result = conn.search(query=q, indices="content")
    data=[]
    for r in result:
        data.append(r)
    return data  

@app.route('/')
def index():

    db = get_db('dev-ethinker')
    last24Hours = datetime.now() - timedelta(hours=12)
    
    pipeTopMentions = [{"$match":{ "date":{"$gt": last24Hours}}},
                                {"$unwind":"$entities"},
                                {"$group":{"_id":"$entities", "count":{"$sum":1}}},
                                {"$sort":{"count":-1}}]

    pipeTopCategories = [{"$match":{ "date":{"$gt": last24Hours}}},
                       {"$unwind":"$tags"},
                       {"$group":{"_id":"$tags", "count":{"$sum":1}}},
                       {"$sort":{"count":-1}}]
    
    mongoData = db.articles.aggregate(pipeTopMentions)
    entities=[]
    for item in mongoData['result'][0:15]:
        dic={}
        dic['entityName']=item['_id']
        dic['mentions']=item['count']
        dic['sentiment']=randint(-10,10)
        entities.append(dic)
    topDailyMentions = { "topDailyMentions": entities}

    mongoDataCat = db.articles.aggregate(pipeTopCategories)
    categories=[]
    for item in mongoDataCat['result'][0:9]:
        dic={}
        dic['categoryName']=item['_id']
        dic['mentions']=item['count']
        dic['sentiment']=randint(-10,10)
        categories.append(dic)
    topDailyCat = { "topDailyCategories": categories}

    articles = db.articles.find({"date":{"$gt": last24Hours}}).count()

    print articles
    return render_template("topDailyMentions.html",
                            articles = articles,
                            mentions = topDailyMentions,
                            categories = topDailyCat,
                            title = "Welcome")
@app.route('/entities')
def entities():    
    if request.args.get('search'):
        query = request.args.get('search')
        print query
    else:
        query="Mariano Rajoy"
    setpoint = datetime.now() - timedelta(hours=500)
    db = get_db('dev-ethinker')
    pipe = [{"$unwind":"$entities"},
            {"$match":{ "entities":query}},
            {"$group":{"_id":{"day": { "$dayOfMonth": "$date" },"month": { "$month": "$date" },"year": { "$year": "$date" },"sentimentCategory":"$sentimentCategory"},
                       "count":{"$sum":1},"sentimentAvg": {"$avg":"$sentimentScore"},"sentimentSum": {"$sum":"$sentimentScore"}}},   
            {"$project":{"day":"$_id.day",
                         "month":"$_id.month",
                         "year":"$_id.year",
                         "sentimentAvg": "$sentimentAvg",
                         "sentimentSum": "$sentimentSum",
                         "mentions":"$count",
                         "sentimentCategory": "$_id.sentimentCategory"}}]

    mongoData = db.articles.aggregate(pipe)
    output=[]
    for item in mongoData['result']:
        dic={}
        dic['date']=str(item["_id"]['year'])+"-"+str(item["_id"]['month'])+"-"+str(item["_id"]['day'])
        dic['totalMentions']=item['mentions']
        if 'sentimentCategory' in item:
            dic['sentimentCategory']=item['sentimentCategory']
        else:
            dic['sentimentCategory']='Neutral'
        dic['totalMentions']=item['mentions']
        dic['sentimentSum']=item['sentimentSum']
        dic['sentimentAvg']=item['sentimentAvg']
        output.append(dic)


    pipeGraph=[{"$match":{ "date":{"$gt": setpoint}}},{"$unwind":"$entities"},{"$unwind":"$tags"},{"$match":{ "entities":query}},
    {"$group":{"_id":{"author":"$author","source":"$titleBlog"},"size":{"$sum":1}}},   
    {"$project":{"author":"$_id.author","source":"$_id.source","size":"$size"}}]  
    mongoDataGraph = db.articles.aggregate(pipeGraph)
    #dataGraph=sorted(mongoDataGraph,key=lambda x:x)
    
    name_to_node = {}    
    root = {'name': query, 'children': [],"size":10}
    i=0
    data=sorted(mongoDataGraph['result'],key=lambda x:x['source'])
    for item in data:
        if i == 0:
            node = {"name":item['source'], 'children':[],"size":5}
            if 'author' in item:
                node["children"].append({'name': item['author'], 'size':item['size']})  
            else:
                node["children"].append({'name': item['source'], 'size':item['size']})              
        else:
            if item['source'] == node['name']:
                if 'author' in item:
                    node["children"].append({'name': item['author'], 'size':item['size']}) 
                else:
                    node["children"].append({'name': item['source'], 'size':item['size']})                   
            else:
                node = {"name":item['source'], 'children':[],"size":5}
                if 'author' in item:
                    node["children"].append({'name': item['author'], 'size':item['size']})
                else:
                    node["children"].append({'name': item['source'], 'size':item['size']})
                root['children'].append(node) 
        i+=1
    
    print root 
    data = {"entityName": query,"sentiments":output }
    return render_template("sentiment.html", 
                            timeseries = data,
                            graph=root,                           
                            title = query)

@app.route('/about')
def about():
    return render_template("about.html",
                            title = "About")

@app.route("/main", methods = ['GET', 'POST'])
def main():
    db = get_db('dev-ethinker')
    if request.args.get('value'):
        value = request.args.get('value')
               
        if value =='categories' :
            pipe = [{"$unwind":"$tags"},{ "$match" : {"$or":[{ "tags" : "Economía" },{ "tags" : "España" },{ "tags" : "Internacional" },{ "tags" : "Tecnología" },{ "tags" : "Política" },{ "tags" : "Sociedad" }]} },
                                        {"$group":{"_id":{"blog": "$tags"},
                                                          "count":{"$sum":1}}},
                                                {"$sort":{"count":-1}}]
            pipeCount = [{ "$group" : { "_id" : None, "count" : { "$sum" : 1 } } }]     
        elif value=='sources':                                        
            pipe = [{"$group":{"_id":{"blog": "$titleBlog"},
                                                "count":{"$sum":1}}},
                                                {"$sort":{"count":-1}}] 
            pipeCount =[{ "$group" : { "_id" : None, "count" : { "$sum" : 1 }}}]

        elif value=='entities': 
            pipe = [{"$unwind":"$entities"},{ "$match" : {"$or":[{ "entities" : "Elena Valenciano"},{ "entities" :"Miguel Arias" }]}},
                                            {"$group":{"_id":{"blog":"$entities"},
                                                          "count":{"$sum":1}}},
                                                {"$sort":{"count":-1}}] 
            pipeCount = [{ "$group" : { "_id" : None, "count" : { "$sum" : 1 } } }] 

        elif value=='author': 
            pipe = [{"$unwind":"$author"},{"$group":{"_id":{"blog": "$author"},
                                                          "count":{"$sum":1}}},
                                                {"$sort":{"count":-1}}]
        elif value=='network': 
            pipe = [{"$unwind":"$entities"},{"$group":{"_id":{"blog": "$entities"},
                                                          "size":{"$sum":1}}}] 
           

    else:    
        pipe = [{"$group":{"_id":{"blog": "$titleBlog"},
                                                "count":{"$sum":1}}},
                                                {"$sort":{"count":-1}}]
        pipeCount = [{ "$group" : { "_id" : None, "count" : { "$sum" : 1 }}}]


    mongoData = db.articles.aggregate(pipe)
    countArticles = db.articles.aggregate(pipeCount)
   
    output=[]
    for item in mongoData['result']:
        dic={}
        if 'month' in item["_id"]:
            dic['date']=str(item["_id"]['month'])+"/"+str(item["_id"]['day'])+"/"+str(item["_id"]['year'])
        if 'blog' in item["_id"]:
            dic['sourceName']=item["_id"]['blog']
        dic['count']=item['count']
        if 'categories' in item["_id"]:
            dic['category']=item["_id"]['categories']
        output.append(dic)  

    from urllib2 import Request, urlopen
    requestAPI = Request("http://devethinker.apiary-mock.com/graph")
    response_body = urlopen(requestAPI).read()
       

    #sorted_output = sorted(output, key=lambda k: k['date'])    
    return render_template("main.html",                                                 
                            data = output,
                            countArt=countArticles['result'][0]['count'],
                            graphData=response_body )    

@app.route('/login', methods = ['GET', 'POST'])
def login(): 
    if request.method =="POST":
        user = request.form['user']
        password = request.form['password']
        db = get_db('dev-ethinker')         
        status = db.users.find({"user":user,"password":password}).count()
        if status == 0:
            message = "Sorry, try another combination"
           # db.users.insert({"user":user,"password":password})
            return render_template("login.html",
                            message=message)
        elif status > 0 :
            message = "Hey, you are succesfully logged in"
            return redirect("/main", code=302) 
       
    elif request.method =="GET":
        return render_template("login.html")

@app.route('/sitemap')
def sitemap():
    url_root = request.url_root[:-1]
    rules = app.url_map.iter_rules()
    return render_template('sitemap.xml', url_root=url_root, rules=rules)

