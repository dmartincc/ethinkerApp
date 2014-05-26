import wikipedia
import nltk.data
import re

sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

#print wikipedia.search("Barack")
#print wikipedia.suggest("Barak Obama")
#print wikipedia.search("Ford", results=3)
#print wikipedia.summary("Apple III", sentences=1)

#a = re.compile("jpg")

def searchWikiPage(keyword):
	output={}
	content = wikipedia.page(keyword)
	senteces=sent_detector.tokenize(content.summary.strip())
	output['title']=content.title.encode('utf-8')
	output['summary']=senteces[0] 
	i=0
	photos=[]
	for item in content.images:
		if '.jpg' in item.lower():
			photos.append(item)
		i+=1
	output['image']=photos[0].encode('utf-8')
	output['url']=content.url.encode('utf-8')
	return output

#print searchWikiPage("Cristiano Ronaldo")