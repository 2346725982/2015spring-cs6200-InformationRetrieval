import time
import re
import requests
import time
import sys
from bs4 import BeautifulSoup
from urlparse import urlparse
from urlparse import urljoin

reload(sys)
sys.setdefaultencoding('utf8')

SEED_PATH = '/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_3/'
FOLDER_PATH = '/Users/Ken/Desktop/crawl/'

class url:
    def __init__(self, currUrl):
        self.url = currUrl
        self.htmlText = ''
        self.cleanedText = []
        self.outlinks = set([])
        self.request = ''

    def visible(self, visited):
        #print self.url
        try:
            self.request = requests.get(self.url)

            return (self.url not in visited and 'html' in self.request.headers['content-type'])
        except ValueError, e:
            return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.TooManyRedirects:
            return False
        except KeyError, e:
            return False
        except Exception as e:
            print "other exceptions", e
            return False

    def crawl(self):
        time.sleep(1)

        ## get htmlText
        self.htmlText = self.request.content
        soup = BeautifulSoup(self.htmlText)

        ## get cleanedText
        for each in soup.find_all('p'):
            self.cleanedText.append(each.get_text())

        ## get outlinks
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                self.outlinks.add(self.canonicalize(link['href']))

    def canonicalize(self, outlink):
        ## point to itself
        if '#' in outlink:
            return self.url

        ## remove ../
        if '..' in outlink:
            return urljoin(self.url, '../c.html')
            
        parse = urlparse(self.url)
        outlinkParse = urlparse(outlink)

        ## no scheme
        if not outlinkParse.scheme:
            scheme = parse.scheme
        else:
            scheme = outlinkParse.scheme

        ## no netloc
        if not outlinkParse.netloc:
            netloc = parse.netloc.lower()
        else:
            netloc = outlinkParse.netloc.lower()

        ## netloc remove port
        if ':' in netloc:
            netloc = netloc.split(':').pop()

        path = outlinkParse.path

        outlink = scheme + '://' + netloc + path

        return urlparse(outlink).geturl()

        
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
            f.write('\n<next_block_of_content>\n')
            f.write(''.join(self.cleanedText)) 
            f.write('\n<next_block_of_content>\n')
            f.write('\n'.join(self.outlinks))
            f.write('\n<next_block_of_content>\n')
            f.write(self.htmlText)
            f.write('\n')

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

    ## initialize by add seeds to frontier
    with open(SEED_PATH + 'seed.txt') as f:
        frontier = f.read().split()

    ## BFS
    start = time.time()
    while frontier and total < 30000:
        curr = frontier.pop()
        u = url(curr)

        if u.visible(visited):
            total += 1
            visited.add(curr)

            print total, curr
            # crawl the current page
            u.crawl()
            u.update(frontier, inlinks, dic, total)
            u.writetoFile(total)
            #u.printOut()
            #print 'frontier', '\n'.join(frontier)
            #print 'visited', '\n'.join(visited)

            if total == 12000:
                with open(FOLDER_PATH + 'inlinks12000', 'w') as f:
                    for each in inlinks:
                        f.write(each)
                        f.write('    ')
                        f.write(';'.join(inlinks[each]))
                        f.write('\n')
    end = time.time()

    with open(FOLDER_PATH + 'inlinks', 'w') as f:
        for each in inlinks:
            f.write(each)
            f.write('    ')
            f.write(';'.join(inlinks[each]))
            f.write('\n')

    print int(end - start)
    print "done."

if __name__ == '__main__' :
    main()
