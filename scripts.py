from unidecode import unidecode
import ast
from selenium import webdriver
import requests
from requests.auth import HTTPProxyAuth
from bs4 import BeautifulSoup
import sys
import os
import ast
from jd import solr_data
from unidecode import unidecode
from mobito import msearch
import xml.etree.ElementTree as ET
from validate import github_validate,stackoverflow_validate,li_extract,youth4work_validate,codechef_validate
import time
import json

requests.packages.urllib3.disable_warnings()

reload(sys)
sys.setdefaultencoding('utf8')
"""
	Use sample_data(query, num) for getting test data from solr, sorted according to verbosity
	get_databin_url(databin, solr_object) returns the url for the databin
	get_all_bins(solr_object) returns all the databin urls


	Validation needs to be improved

"""

def stack_elastic_search(term, num):
	url = "http://104.155.143.103:9200/stackoverflow/profile/_search?size" + str(num) +"&q=" + str(term)
	start = time.time()
        r = requests.get(url)
        print "STACK DATA RECIEVED AT %.2f" % (time.time() - start)
        data = json.loads(r.content)

        data = data['hits']['hits']
        act_list = []
        for i in data:
                t = i['_source']
                #dat = dict([(str(k), str(v)) for k, v in t.items()])
                act_list.append(t)
        return act_list


def elastic_search(term, num):
	url = 'http://104.155.143.103:9200/people-india/profile/_search?size='+ str(num) +'&q=' + term
	start = time.time()
	r = requests.get(url)
	print "DATA RECIEVED AT %.2f" % (time.time() - start)
	data = json.loads(r.content)
	
	data = data['hits']['hits']
	act_list = []
	for i in data:
		t = i['_source']
		#dat = dict([(str(k), str(v)) for k, v in t.items()])
		act_list.append(t)
	return act_list
	
	
def remove_non_ascii(text):
    return unidecode(unicode(text, encoding = "utf-8"))

def sample_data(query, num):
	print "sample data started.."
	return verbose_sort(clean(solr_data(query, num)))

def url_validate(url, a, databin):
	
	li = li_extract(a)
	print "Validation started for %s in %s " %(a['full_name'], url)
	score = 0
	name = a['full_name']
	uni_name = "eoueorueuroeroi"
	city_name = "oeuirowieropio"
	org_name = "roitoeirtoier"

	try:
		uni_name = a['education'][0]['name']
	except:
		pass

	try:
		city_name = a['locality'].split(" ")[0]
	except:
		pass

	try:
		org_name = a['experience'][0]['organization'][0]['name']
	except:
		pass

	#r = requests.get(url)
	if "http" not in url:
		url = "https://"+url
	r = req(url)

	if name.lower() in r.content.lower():
		score += 2

	if uni_name.lower() in r.content.lower():
		score += 1

	if city_name.lower() in r.content.lower():
		score += 1

	if org_name.lower() in r.content.lower():
		score += 1

	#print "score: " + str(score) + " " + url

	if "github" in databin:
		if score > 1:
			return github_validate(r,li)

	if "stackoverflow" in databin:
		if score > 1:
			return stackoverflow_validate(r, li)

	if "codechef" in databin:
		if score > 1:
			return codechef_validate(r, li)

	if "spoj" in databin:
		if score > 2:
			return True

	if "quora" in databin:
		if score > 1:
			return True

	if "youth4work" in databin:
		if score > 2:
			return youth4work_validate(r, li)

	if "hackerrank" in databin:
		if score > 2:
			return True

	if "kaggle" in databin:
		if score > 1:
			return True

	if "analytics vidhya" in databin:
		if score > 1:
			return True

	if "techgig" in databin:
		if score > 1:
			return True

	if 'wordpress' in databin:
		if score > 1:
			return True
	if 'blogspot' in databin:
		if score > 1:
			return True

	if 'coderwall' in databin:
		if score > 1:
			return True
	if 'about.me' in databin:
		if score > 1:
			return True

	if 'researchgate' in databin:
		if score > 1:
			return True
	if 'githubio' in databin:
		if score > 1:
			return True


	return False


def fix(url, key):

	h = '/'
	if "http" not in url:  #For stackoverflow
                url = "https://"+url

	try:
		if key == 'blogspot.com' or key == 'wordpress.com' or key == 'github.io':
			a = url.replace('?','/').strip('/').split('/')
		        last = a[-1]
		        while( key not in last):
		                a.pop()
		                last = a[-1]
		        url = h.join(a)
			return url


		a = url.replace('?','/').strip('/').split('/')
		second_last = a[-2]
		while(second_last != key ):
			a.pop()
			second_last = a[-2]
		url = h.join(a)
	except:
		return 'None'

	return url

databinmap = {
	"github":"github.com",
	"stackoverflow": "stackoverflow.com/users",
	"codechef":"codechef.com/users",
	"spoj": "spoj.com/users",
	"hackerrank": "hackerrank.com",
	"quora": "quora.com/profile",
	"youth4work": "youth4work.com/y/",
	"kaggle": "kaggle.com",
	"analytics vidhya": "analyticsvidhya.com/user/profile",
	"techgig": "techgig.com",
	'hackerearth':'www.hackerearth.com',
	'twitter':'twitter.com',
	'about.me':'about.me',
	'researchgate': 'www.researchgate.net',
	'coderwall':'coderwall.com',
	'bitbucket': 'bitbucket.org',
	'blogspot': 'blogspot.com',
	'wordpress':'wordpress.com',
	'angel.co':'angel.co',
	'twitter':'twitter.com',
	'githubio':'github.io'
}


second_last_word = {
	'github': 'github.com',
	'quora': 'profile',
	'hackerrank':'www.hackerrank.com',
	'codechef': 'users',
	'stackoverflow': 'users',
	'spoj': 'users',
	'youth4work': 'y',
	'hackerearth': 'www.hackerearth.com',
	'kaggle': 'www.kaggle.com',
	'analytics vidhya': 'profile',
	'techgig': 'www.techgig.com',
	'twitter':'twitter.com',
	'about.me':'about.me',
	'twitter':'twitter.com',
	'researchgate':'profile',
	'coderwall':'coderwall.com',
	'bitbucket':'bitbucket.org',
	'angel.co': 'angel.co',
	'blogspot': 'blogspot.com',
	'wordpress':'wordpress.com',
	'githubio':'github.io'
}




def get_databin_url(databin, a):
	print "Started " + databin + " for " + a['full_name']
	name = a['full_name']
	plus = "+"
 	name = plus.join(name.split(" "))
 	#url = "https://www.google.com/search?q=" + name + "+" +  databin


	##speacial case for github

	if databin == 'github':
		print "github"
		url = "https://github.com/search?q=" + name + "&type=Users"
		time.sleep(5)
		r = requests.get(url)
		tree = BeautifulSoup(r.content)
		print url
		print r
		divs = tree.find_all('div', attrs={'class':'user-list-info ml-2'})
		for i in divs:
			url = "https://github.com" + i.find('a')['href']
			print url
			if url_validate(url, a, databin):
				print "URL VALIDATED FOR :%s" % url
				return url, []
		return "None", []

 	dat = databinmap[databin]
	url = "https://www.google.com/search?q=" + name + "+inurl:" +  databinmap[databin]
	search_term = name + " " + databin
	urls_all = []
	try:
 		#r = requests.get(url)
		#request = req(url)
		#print request
		#if request.status_code != 200:
		#	get_databin_url(databin, a)
		#c = remove_non_ascii(request.content)
 		#r = BeautifulSoup(c, 'lxml')
		#t = r.body.find_all('cite', attrs={'class':'_Rm'})
		
		t = []
		r = msearch(search_term)
		print r
		root = ET.fromstring(r.content)
		for child in root[1]:
			for c in child:
				if c.tag == 'display_url':
					t.append(c)

		print "urls found " + str(len(t))
		# all urls
		#urls_all = []
		#print "yes"
		for i in t:
			if dat in i.text:
				fixed_url = fix(i.text, second_last_word[databin])
				if fixed_url == 'None':
					continue
				urls_all.append(fixed_url)

		for fixed_url in urls_all:
			if url_validate(fixed_url, a, databin):
				print "URL VALIDATED FOR " + databin + ": " + fixed_url
				return fixed_url, urls_all

	except Exception as e:
		print e

	return 'None', urls_all
				
	#try:
 		#r = requests.get(url)
		#print "url request fulfilled"
		#try:
 		#	lines = r.content.replace("<", ">").split(">")
		#except:
		#	print "error with splitting"
		#print url
		#print len(lines)
		#for i in lines:
			#print i
			#print dat
		#	if dat in i:
		#		print "dat in line"
		#		url = "null"
		#		try:
		#			url = i.split('"')[1].split("=")[1].split("&")[0]
		#		except:
		#			print "couldn't fetch url"
		#			continue
		#		if url is not "null":
		#			print url
		#			if url_validate(url, a, databin):
		#				return url


	#except Exception as e: print(e)


from threading import Thread
import Queue


def get_all_bins(a):
	databin_list = [
		#'codechef',
		#'stackoverflow',
		#'hackerrank',
		#'spoj',
		#'quora',
		#'youth4work',
		'github',
		#'kaggle',
		#'techgig',
		#'analytics vidhya',
		#'bitbucket',
		#'coderwall',
		#'researchgate',
		#'blogspot',
		#'wordpress',
		#'about.me',
		#'githubio',
		#'twitter'
		
	]
	url_dict = {}
	'''
	que = Queue.Queue()
	thread_list = []
	url_list = []

	for dat in databin_list:
		#url_dict[dat], t = thread.start_new_thread(get_databin_url, (dat, a))
		t = Thread(target=lambda q, arg1, arg2: q.put(get_databin_url(arg1, arg2)), args=(que, dat, a))
		t.start()
		thread_list.append(t)

	for t in thread_list:
		t.join()

	while not que.empty():
		url_list.append(que.get()[0])
	'''
	for dat in databin_list:
		url_dict[dat], t = get_databin_url(dat, a);
	return url_dict



def stackoverflow_validate(url, a):
	return True

def stackoverflow_crawl(a):
	name = a['full_name']
	plus = "+"
 	name = plus.join(name.split(" "))
	url = "http://www.google.com/search?q=" + name + "Stackoverflow"
	r = requests.get(url)
 	#r = req(url)
 	lines = r.content.replace("<", ">"). split(">")
 	for i in lines:
 		if "stackoverflow.com/users" in i:
 			url = i.split('"')[1]
 			if stackoverflow_validate(url, a):
 				return url
 	return None


def github_validate(url, a):
	return True

def github_crawl(a):
	data = {}
 	name = a['full_name']
 	plus = "+"
 	name = plus.join(name.split(" "))
 	url = "https://github.com/search?q=" + name + "&type=Users&utf8=%E2%9C%93"
 	r = requests.get(url)
 	#r = req(url)
 	l = r.content.split("\n")
 	links = []
 	for i in range(len(l)):
 		if "user-list-info" in l[i]:
 			url = "https://github.com" + l[i+1].split('"')[1]
 			if github_validate(url, a):
 				return url

 	return 'None' 




'''
def req(url):
	proxy_host = "proxy.crawlera.com"
	proxy_port = "8010"
	proxy_auth = HTTPProxyAuth("f9f54a74a3f44b7b977490541df22662", "")
	proxies = {"https": "https://{}:{}/".format(proxy_host, proxy_port), "http":"http://{}:{}/".format(proxy_host, proxy_port)}
	r = requests.get(url, proxies=proxies, auth=proxy_auth, verify='crawlera-ca.crt')
	return r
'''

def req(url):
	r = requests.get(url)
	return r


	
def clean(a):
	a_list = []
	for i in a:
		a_list.append(ast.literal_eval(i))
	return a_list


def verbose_sort(a):
	len_list = []
	for i in a:
		len_list.append(len(str(i).split(" ")))
	return [x for (y,x) in sorted(zip(len_list, a), reverse = True)]


def crawl(a, driver):

	links = []
	name = a['full_name']
	try:
		org_name = a['experience'][0]['organization'][0]['name']
	except:
		org_name = ""

	try:
		uni_name = a['education'][0]['name']
	except:
		uni_name = ""

	grad_year =  int(a['education'][0]['end'])


	data_bins = ["Github", "Kaggle", "Codeforces", "Codechef", "Stackoverflow", "Youth4work", "Naukri"
				,"Quora", "about.me", "techgig", "analytics vidhya", "data camp", "apoj", "angel.co",
				]
	for data in data_bins:
		driver.get("https://www.google.co.in/search?q=" + name + " " + data)
		try:
			results = driver.find_elements_by_class_name("g")
			links.append(results[0].find_element_by_tag_name("a").get_attribute("href"))
		except:
			continue

	for data in data_bins:
		if org_name == "":
			break
		if grad_year > 2010:
			org_name = uni_name
		driver.get("https://www.google.co.in/search?q=" + name + " " + org_name + " " + data)
		try:
			results = driver.find_elements_by_class_name("g")
			links.append(results[0].find_element_by_tag_name("a").get_attribute("href"))
		except:
			continue

	return links



