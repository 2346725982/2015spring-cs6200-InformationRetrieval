import elasticsearch
from elasticsearch import client
from elasticsearch import Elasticsearch
from elasticsearch.client.cat import CatClient


FOLDER_PATH = '/Users/Ken/Desktop/crawl/'

es = elasticsearch.Elasticsearch("localhost:9200", timeout=600, maxRetry=2, revival_delay=0)
index = elasticsearch.client.IndicesClient(es)
catClient = elasticsearch.client.CatClient(es)

def deleteIndex ():
    index.delete('*')

def createIndex():
    index.create(index='ap_dataset',
        body={
                   "settings": {
                     "index": {
                       "store": {
                         "type": "default"
                       },
                       "number_of_shards": 1,
                       "number_of_replicas": 1
                     },
                     "analysis": {
                       "analyzer": {
                         "my_english": { 
                           "type": "english",
                           "stopwords_path": "stoplist.txt" 
                         }
                       }
                     }
                   }
                 })
 
    index.put_mapping(index='ap_dataset', doc_type = 'document', body={
                                   "document": {
                                     "properties": {   
                                     "docno": {
                                         "type": "string",
                                         "store": True,
                                         "index": "not_analyzed"
                                       },
                                     "text": {
                                         "type": "string",
                                         "store": True,
                                         "index": "analyzed",
                                         "term_vector": "with_positions_offsets_payloads",
                                         "analyzer": "my_english"
                                       },
                                     "inlinks": {
                                         "type": "string",
                                         "store": True,
                                         "index": "no"
                                       },
                                     "outlinks": {
                                         "type": "string",
                                         "store": True,
                                         "index": "no"
                                       }
                                     } 
                                   }   
                                 })

def readEachFile(i, inlinks):
    global es
    with open(FOLDER_PATH + str(i), 'r') as f:
        content = f.read().split('<next_block_of_content>\n')

        tmp_inlinks = set()
        tmp_inlinks = tmp_inlinks.union(set(inlinks[content[0].strip()]))

        try:
            check = es.get( index = 'ap_dataset', doc_type = 'document', id = content[0].strip() )
            tmp_inlinks = tmp_inlinks.union(set(check['_source']['inlinks'].split('\n')))
        except Exception:
            pass
        finally: 
            es.index(
                index = 'ap_dataset',
                doc_type = 'document',
                id = content[0].strip(), 
                body = {
                    'docno' : content[0].strip(),
                    'text' : content[1],
                    'outlinks' : content[2],
                    'inlinks' : '\n'.join(tmp_inlinks)
                    #'html' : content[3]
                }
            )

def main():
    #deleteIndex()
    #createIndex()
    total = 12100
    inlinks = {}

    with open(FOLDER_PATH + 'inlinks12000', 'r') as f:
        for line in f:
            tmp = line.split('    ')
            try:
                inlinks[tmp[0].strip()] = tmp[1].split(';')
            except Exception:
                #print line
                inlinks[tmp[0].strip()] = []
    

    for i in range(1, total):
        print i
        readEachFile(i, inlinks)

if __name__ == '__main__':
    main()
