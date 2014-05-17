# -*- coding: utf-8 -*
import json, feedparser, nlpModules, time,datetime
from pattern.web import URL, DOM, plaintext, strip_tags, decode_entities


blogs=['http://ep00.epimg.net/rss/elpais/portada.xml',
		'http://www.abc.es/rss/feeds/abcPortada.xml']
       
def get_db_es(db_name):
    import pyes 
    conn = pyes.ES('http://dwalin-us-east-1.searchly.com/',
				basic_auth={'username': 'dev', 'password' : 'oqozmjudhxtbeagkjqzvj15tarseebyd'})
    return conn

def get_db(db_name):
    from pymongo import MongoClient
    uri = 'mongodb://user:passw0rd@oceanic.mongohq.com:10024/dev-ethinker'
    client = MongoClient(uri)
    db = client[db_name]
    return db      

def blogsData(blogs,time,db):		
	
	d = feedparser.parse(blogs)	
	
	dicS = {}
	dicS['rssLink'] = blogs
	dicS['titleBlog'] = d['feed']['title'].encode('utf-8').replace("\xe2\x80\x99","'")
	dicS['descriptionBlog'] = d['feed']['description'].encode('utf-8').replace("\xe2\x80\x99","'")
	dicS['updated'] = d['feed']['updated'].encode('utf-8')	
	db.sources.update({"titleBlog":dicS['titleBlog']},dicS,upsert=True)
		
	for item in d['entries']:
		dic = {}
		dic['titlePost'] = item.title.encode('utf-8').replace("\xe2\x80\x99","'")
		if db.articles.find({"titlePost":dic['titlePost']}).count() == 0:
			dic['titleBlog'] = d['feed']['title'].encode('utf-8').replace("\xe2\x80\x99","'")
			dic['descriptionBlog'] = d['feed']['description'].encode('utf-8').replace("\xe2\x80\x99","'")		
			dic['link'] = item.link.encode('utf-8')
			dic['date']=datetime.datetime.utcnow()
			if "author" in item:
				dic['author'] = item.author.encode('utf-8').replace("(","").replace(")","")
			#Detag content, define parsing rules for outfits and
			#set nltk process
			if "content" in item:
				text = plaintext(item.content[0]['value'])
				dic['content'] = text.encode('utf-8').replace("\xe2\x80\x99","'").replace("\n"," ").replace(":"," ")
				dom = DOM(item.content)
				imagesUrl = []
				for e in dom('img'):
					imagesUrl.append(e.attributes.get('src','').encode('utf-8'))
				dic['images'] = imagesUrl
				dic['entities']=nlpModules.extract_entities_regex(dic['titlePost']+" "+text.encode('utf-8'))
				sentiment=nlpModules.sentimentAnalysis(text.encode('utf-8'))
				dic['sentimentScore']=sentiment[0]
				dic['sentimentCategory']=sentiment[1]
			elif item.summary:
				text = plaintext(item.summary)
				dic['content'] = text.encode('utf-8').replace("\xe2\x80\x99","'").replace("\n"," ").replace(":"," ")
				dom = DOM(item.description)
				imagesUrl = []
				for e in dom('img'):
					imagesUrl.append(e.attributes.get('src','').encode('utf-8'))
				dic['images'] = imagesUrl
				dic['entities']=nlpModules.extract_entities_regex(dic['titlePost']+". "+text.encode('utf-8'))
				sentiment=nlpModules.sentimentAnalysis(text.encode('utf-8'))
				dic['sentimentScore']=sentiment[0]
				dic['sentimentCategory']=sentiment[1]
			if item.published:
				dic['published'] = item.published.encode('utf-8')			
			if "tags" in item:
				tags = []
				for tag in  item.tags:
					tags.append(tag.term.encode('utf-8'))
				dic['tags'] = tags	
			#db.articles.insert(dic)
			db.articles.update({"titlePost":dic['titlePost']},dic,upsert=True)
		
def main():
	db = get_db('dev-ethinker')	
	mongoData = db.sources.find()	
	for blog in mongoData:
		blogsData(blog['rssLink'],blog['updated'],db)
		

if __name__ == '__main__':

	main()

