# -*- coding: utf-8 -*-
from flask import render_template,request,redirect
from flask import jsonify
from app import app
import json, time, random, re, datetime
from datetime import datetime, timedelta
from random import randint
import calendar
from operator import itemgetter


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

@app.route('/',methods = ['GET', 'POST'])
def index():
    if request.method =="POST":
        return redirect("/main", code=302) 

    else:   
        return render_template("landingpage.html",
                                articles = [],
                                mentions =  [],
                                categories = [],
                                title = "Welcome")

@app.route("/main", methods = ['GET', 'POST'])
def main():
    db = get_db('dev-ethinker')    
    output=[]    
    if request.args.get('value'):
        value = request.args.get('value') 
        if request.args.get('search'):               
            query = request.args.get('search')  
        else:
            query="Elena Valenciano"         
               
        if value =='summary':
            sourcesPipe = [{"$unwind":"$entities"},{"$match":{ "entities":query}},
                                            {"$group":{"_id":{"key":"$titleBlog"},
                                                          "values":{"$sum":1}}},
                                                {"$project":{"key":"$_id.key","values":"$values"}},
                                                {"$sort":{"values":-1}}] 
            categoriesPipe = [{"$unwind":"$entities"},{"$unwind":"$tags"},
                                            {"$match":{ "entities":query}},
                                            {"$group":{"_id":{"text":"$tags"},
                                                          "size":{"$sum":1}}},
                                                {"$project":{"text":"$_id.text","size":"$size"}},
                                                {"$sort":{"size":-1}}] 

            articlesPipe = [{"$unwind":"$entities"},{"$match":{ "entities":query}},
                                            {"$group":{"_id":{"key":"$entities"},
                                                          "count":{"$sum":1},"sentimentAvg": {"$avg":"$sentimentScore"},"sentimentSum": {"$sum":"$sentimentScore"}}},
                                            {"$project":{"key":"$_id.key","count":"$count","sentimentAvg":"$sentimentAvg","sentimentTotal":"$sentimentSum"}}]
            sentimentPipe = [{"$unwind":"$entities"},{"$match":{ "entities":query}},
                                            {"$group":{"_id":{"key":"$entities"},
                                                          "values":{"$sum":1}}},
                                            {"$project":{"key":"$_id.key","values":"$values"}},
                                            {"$sort":{"values":-1}}]  

            sourcesData = db.articles.aggregate(sourcesPipe)
            categoriesData = db.articles.aggregate(categoriesPipe)
            articlesData = db.articles.aggregate(articlesPipe)
            output ={"sources": sourcesData['result'],
                    "categories": categoriesData['result'][0:25],
                    "articles": articlesData['result'][0]['count'],
                    "sentimentAvg": int(articlesData['result'][0]['sentimentAvg']),
                    "sentimentTotal": articlesData['result'][0]['sentimentTotal']}
            message="Summary data about the entity, number of mentions, global sentiment, sources and content"


        elif value=='mentions' or value=='sentiment':                                        
            pipe = [{"$unwind":"$entities"},
                    {"$match":{ "entities":query}},
                    {"$group":{"_id":{"day": { "$dayOfMonth": "$date" },"month": { "$month": "$date" },"year": { "$year": "$date" }},
                               "count":{"$sum":1},"sentimentAvg": {"$avg":"$sentimentScore"},"sentimentSum": {"$sum":"$sentimentScore"}}},   
                    {"$project":{"day":"$_id.day",
                                 "month":"$_id.month",
                                 "year":"$_id.year",
                                 "sentimentAvg": "$sentimentAvg",
                                 "sentimentSum": "$sentimentSum",
                                 "mentions":"$count"}}]
            mongoData = db.articles.aggregate(pipe)
            dataOutput=[]
            for item in mongoData['result']:
                dic={}
                date=str(item["_id"]['day'])+"-"+str(item["_id"]['month'])+"-"+str(item["_id"]['year'])                
                dic['date']=datetime.strptime(date, '%d-%m-%Y')
                tupleDate=datetime.timetuple(dic['date'])                
                milliDate=calendar.timegm(tupleDate)*1000             
                dic['milliseconds']= long(milliDate)
                dic['totalMentions']=item['mentions']
                dic['sentimentSum']=item['sentimentSum']
                dic['sentimentAvg']=item['sentimentAvg']
                dataOutput.append(dic)            
            sortData=sorted(dataOutput, key=lambda x:x['date']) 
            if value=="mentions":           
                output=[{'key':"Total Mentions","values":[]}]
                message="Time serie of mentions about an entity"
                for item in sortData:
                    output[0]['values'].append([item['milliseconds'],item['totalMentions']])
            elif value=="sentiment":
                output=[{'key':"Total Sentiment","values":[]},{'key':"Average Sentiment","values":[]}]
                message="Time serie of global and average sentiment about an entity"
                for item in sortData:
                    output[0]['values'].append([item['milliseconds'],item['sentimentSum']])
                    output[1]['values'].append([item['milliseconds'],item['sentimentAvg']])

        elif value =='sources': 
            pipe = [{"$unwind":"$entities"},{ "$match" : {"$or":[{ "entities" : "Elena Valenciano"},{ "entities" :"Miguel Arias" }]}},
                                            {"$group":{"_id":{"blog":"$entities"},
                                                          "count":{"$sum":1}}},
                                                {"$sort":{"count":-1}}] 
            pipeCount = [{ "$group" : { "_id" : None, "count" : { "$sum" : 1 } } }] 

        elif value =='network': 
            pipeGraph=[{"$unwind":"$entities"},{"$unwind":"$tags"},{"$match":{ "entities":query}},
            {"$group":{"_id":{"author":"$author","source":"$titleBlog"},"size":{"$sum":1}}},   
            {"$project":{"author":"$_id.author","source":"$_id.source","size":"$size"}}]  
            mongoDataGraph = db.articles.aggregate(pipeGraph)
            #dataGraph=sorted(mongoDataGraph,key=lambda x:x)
            message="Mentions network about an entity, main node is the entity, first level are sources and second level influencers"
            name_to_node = {}    
            output = {'name': query, 'children': [],"size":10}
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
                            node["children"].append({'name': item['source'], 'size':5})                   
                    else:
                        node = {"name":item['source'], 'children':[],"size":5}
                        if 'author' in item:
                            node["children"].append({'name': item['author'], 'size':item['size']})
                        else:
                            node["children"].append({'name': item['source'], 'size':5})
                        output['children'].append(node) 
                i+=1    
    else:
        query="No Entity"
        value="" 
    
     
   
    import wikiSearch as ws
    try:
        response_body=ws.searchWikiPage(query)
    except:
        response_body=[]    
    
    return render_template("content.html",
                            message=message,
                            title = query,
                            value = value,                                                 
                            data = output,
                            bio = response_body)

@app.route('/login', methods = ['GET', 'POST'])
def login(): 
    if request.method =="POST":
        user = request.form['user']
        password = request.form['password']
        db = get_db('dev-ethinker')         
        status = db.users.find({"user":user,"password":password}).count()
        user = db.users.find({"user":user,"password":password})        
        if status == 0:
            message = "Ups, it seems you don´t know your password or user"
           # db.users.insert({"user":user,"password":password})
            return render_template("login.html",
                                    message=message)
        elif status > 0  and user[0]['iduser']<101:
            message = "Hey, you are succesfully logged in"
            return redirect("/search", code=302) 
        elif status > 0  and user[0]['iduser']>=101:
            message = "Ups, sorry but we are in a private beta and we have rescrticted the access to the first 100 users. We will get in touch with you when we will launch ethinker to outter space."
            return render_template("login.html",
                                    message=message)       
    elif request.method =="GET":
        return render_template("login.html",
                                title="Login")

@app.route('/signup', methods = ['GET', 'POST'])
def signup(): 
    if request.method =="POST":
        user = request.form['user']
        password = request.form['password']
        email = request.form['email']
        db = get_db('dev-ethinker')   
        users = db.users.find().count()
        status = db.users.find({"user":user,"email":email}).count()        
        if users < 101:
            if status == 0:            
                db.users.insert({"user":user,"password":password,"email":email,"iduser":users+1})
                return redirect("/search", code=302)                  
            elif status > 0 :      
                message = "Ups, sorry but that users or email are already register." 
                return render_template("signup.html",
                                        message=message)
        else:
            message = "Ups, sorry but we are in a private beta and we have rescrticted the access to the first 100 users. We will get in touch with you when we will launch ethinker to outter space."
            if status == 0:            
                db.users.insert({"user":user,"password":password,"email":email,"iduser":users+1})                               
            elif status > 0 :      
                message = "Ups, sorry but that users or email are already register."         
            return render_template("signup.html",
                                    message=message)
        
       
    elif request.method =="GET":
        return render_template("signup.html",
                                title="Sign Up to ethinker")

@app.route('/search')
def search():  
    db = get_db('dev-ethinker')
    trends = db.trends.find().sort("date",-1).limit(1)          
    return render_template("search.html",
                            title="Search",
                            data=trends[0])

@app.route('/about')
def about():
    return render_template("about.html",
                            title = "About")

@app.route('/sitemap')
def sitemap():
    url_root = request.url_root[:-1]
    rules = app.url_map.iter_rules()
    return render_template('sitemap.xml',
                            url_root=url_root, 
                            rules=rules)

