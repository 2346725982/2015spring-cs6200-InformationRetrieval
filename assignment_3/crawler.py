import time
import re
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse

SEED_PATH = '/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_3/'
FOLDER_PATH = '/Users/Ken/Desktop/crawl/'

class url:
    def __init__(self, currUrl):
        self.url = currUrl
        self.htmlText = ''
        self.cleanedText = ''
        self.outlinks = set([])
        self.request = requests.get(currUrl)

    def visible(self, visited):
        return self.url not in visited and 'html' in self.request.headers['content-type']

    def crawl(self):
        time.sleep(0.1)

        ## get htmlText
        self.htmlText = self.request.content
        soup = BeautifulSoup(self.htmlText)

        ## get cleanedText
        self.cleanedText =  soup.get_text('\n', strip = True).encode('utf-8').strip()
        
        ## get outlinks
        alinks = soup.find_all('a')
        #self.outlinks = [l.get('href') for l in alinks] 
        for link in alinks:
            if link.has_attr('href'):
                self.outlinks.add(self.canonicalize(link['href']).encode('utf-8'))
                #print self.canonicalize(link['href'])

    def canonicalize(self, url):
        if not urlparse(url).netloc:
            url = urlparse(self.url).netloc + url

        if not urlparse(url).scheme:
            url = 'http://' + url

        return urlparse(url).geturl()
        
    def update(self, frontier, inlinks, dic, total):
        for ele in self.outlinks:
            ## update frontier
            frontier.insert(0, ele)

            ## update inlinks
            if ele not in inlinks:
                inlinks[ele] = []
            inlinks[ele].append(self.url)

            ## update dic
            dic[total] = self.url

    def writetoFile(self, total):
        with open(FOLDER_PATH + str(total), 'w') as f:
            f.write(self.url)
            f.write(self.htmlText)
            f.write(self.cleanedText)
            f.write('\n'.join(self.outlinks))

    def printOut(self):
        #print self.url
        #print self.htmlText
        #print self.cleanedText
        print '\n'.join(self.outlinks)

def main():
    total = 0
    frontier = []
    visited = set([])
    inlinks = {}
    dic = {}

    with open(SEED_PATH + 'seed.txt') as f:
        frontier = f.read().split()

    while frontier and total < 30 :
        curr = frontier.pop()
        u = url(curr)

        if u.visible(visited):
            print curr
            total += 1
            visited.add(curr)

            # crawl the current page
            u.crawl()
            u.update(frontier, inlinks, dic, total)
            u.writetoFile(total)
            #u.printOut()
            #print 'frontier', '\n'.join(frontier)
            #print 'visited', '\n'.join(visited)

    print "done."

if __name__ == '__main__' :
    main()
