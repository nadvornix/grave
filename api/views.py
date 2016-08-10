#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.views.decorators.cache import cache_page

from xml.etree import ElementTree as ET
import threading
import sys
import datetime
from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader

import socket
socket.setdefaulttimeout(15)
from urllib import urlopen
from time import sleep
import os.path,time
import shelve
from pprint import pprint
'''
TODO:
- celkovy pocet hledanych tweetu
- aby se srovnali podle data
- design vysledku
- zmenit cestu k shelve nekam ke mne
- mikroformaty ?
- tabindex, pro focus
- html entity

DEPLOY:
- cesta k shelvovacimu souboru
- cache timeout
- pocet prohledavanych polozek
'''
class NS:
    def __init__(self, uri):
         self.uri = uri
    def __getattr__(self, tag):
         return self.uri + tag
    def __call__(self, path):
         return "/".join(getattr(self, tag) for tag in path.split("/"))
ATOM=NS("{http://www.w3.org/2005/Atom}")
TWITTER=NS("http://api.twitter.com/")

class Chybovnicek ():
    chyba=''
chybovnicek = Chybovnicek()

def search(i,nalezeny,nick):
    url='http://search.twitter.com/search.atom?q=from:%s&rpp=200&page=%s' % (nick,i+1)
    print url
    try:
        f = urlopen(url)
    except (IOError, socket.error):
        chybovnicek.chyba ='AAAAAAAAA Nemohu se spojit se serverem twitteru, zkuste to prosím později.'
        return
    tree= ET.fromstring(f.read())

    for entry in tree.findall(ATOM("entry")):
        nalezeny.append(entry)
        
def feed(publikovany,nick,zbyva):
    try:
        url = 'http://twitter.com/statuses/user_timeline/%s.atom?count=200' % (nick)
        print url
        f = urlopen(url)
    except (IOError, socket.error):
        chybovnicek.chyba ='BBB Nemohu se spojit se serverem twitteru, zkuste to prosím později.'
        return
        
    tree= ET.fromstring(f.read())
    for entry in tree.findall(ATOM("entry")):
        elem = entry.find(ATOM('id'))
        cislo = elem.text.split('/')[-1]
        publikovany.append(cislo)

    try:
        zbyva = f.headers['X-RateLimit-Remaining']
    except KeyError:
        zbyva="?"
    print 'zbyva',zbyva

def loguj(nick,zbyva):
    zbyva=0
    f = open('twitter.log','a')
    f.write('nick:%s    datum:%s    zbyva:%s\n'%(nick,datetime.datetime.now(), zbyva))
    f.close()

    print 

#@cache_page(60 * 30)
def index(request, nick, format="web"):
    context = {}

    zbyva=0
    context['nick'] = nick
    publikovany = []
    nalezeny = []
    smazany = []

    try:
        d = shelve.open('twit')
        stari = time.time()-d[str('%s-time'%nick)]
        print stari,'vterin stary'
        if stari > 60*60*1:
            raise 'moc stary'
        smazany=d[str(nick)]
        print 'Z CACHE'
        
        smazany = map(ET.fromstring, smazany)
        pprint (smazany)
    except :
        print sys.exc_info()


        print 'vice jak 15 minut, nebo chyba'

        #z normalniho feedu:
        a=threading.Thread(target = lambda : feed(publikovany,nick,zbyva) ).start()

        #z vyhledavani:
        vlakna=[]
        for i in range(1):
            vlakna.append(threading.Thread(target = lambda : search(i, nalezeny, nick) ).start())

        while threading.activeCount()>2:
            sleep(0.1)
        print len(nalezeny),len(publikovany),len(nalezeny)*len(publikovany)
        if len(nalezeny)*len(publikovany)==0:
            chybovnicek.chyba = u'Chyba spojení se serverem Twitteru, zkuste to prosím později'

        chyba=chybovnicek.chyba
        

            
        print chyba
        print len(nalezeny),'nalezenych'
        print len(publikovany),'publikovanych'
        print chyba

        if chyba:
            context['chyba']=chyba
            t = loader.get_template('api/web.html')
            c = RequestContext(request,context)
            return HttpResponse(t.render(c))


        for entry in nalezeny:
            elem = entry.find(ATOM('id'))
            cislo = elem.text.split(':')[-1]
            if not cislo in publikovany:
                smazany.append(entry)

        pprint (smazany)
        smazanyXml = map(ET.tostring, smazany)

        d = shelve.open('twit')

        d[str(nick)]=smazanyXml
        d[str('%s-time'%(nick))]=time.time()
        d.close()


    threading.Thread(target = lambda : loguj(nick,zbyva) ).start()
    chyba=chybovnicek.chyba
    print chyba
    print len(nalezeny)
    print len(publikovany)
    print chyba




    results=[]
    for element in smazany:
        tweet={}

        text = element.find(ATOM('content')).text

        text=text.encode('utf-8')
        tweet['text']=text
        for link in element.findall(ATOM('link')):
            if link.attrib['type'].startswith('image'):
                tweet['image'] = link.attrib['href']
            elif link.attrib['type'].startswith('text/html'):
                tweet['link'] = link.attrib['href']
        tweet['nick'] = nick
        tweet['source'] = element.find('{http://api.twitter.com/}source').text

        published =  element.find(ATOM('published')).text

        tweet['created_at'] = datetime.datetime.strptime(published.strip(), '%Y-%m-%dT%H:%M:%SZ')

        results.append(tweet)


    if not results:         #TODO:zmenit počet tweetu, taky změnit v šabloně api/web.html
        context['chyba'] = 'Nevidím žádné smazané tweety (prohledávám pouze posledních 200 tweetu)'
    context['results'] = results
    if format=='xml':
        t = loader.get_template('api/xml.html')
        c = RequestContext(request,context)
        return HttpResponse(t.render(c), mimetype="application/xml")
    elif format=='json':
        t = loader.get_template('api/json.html')
        c = RequestContext(request,context)
        return HttpResponse(t.render(c), mimetype="text/plain")
    else:
        t = loader.get_template('api/web.html')

    c = RequestContext(request,context)
    return HttpResponse(t.render(c))
