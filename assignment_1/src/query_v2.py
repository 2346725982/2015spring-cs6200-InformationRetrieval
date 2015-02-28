#! /usr/bin/python

import math
import time
import operator
from elasticsearch import Elasticsearch

meaningless_word = {"Document", "will", "or", "a", "of", "the", "on", "something", "by", "about", "with", "as", "to", "over", "either", "which", "in", "how", "and", "identify", "one", "discuss", "report", "include", "some", "an", "any", "has", "at", "must", "being", "against", "into", "its", "used", "certain", "US","\"dual-use\"", "even", "other", "been", "doing", "since", "use", "both", "d'etat", "actual" }

QUERY_PATH = "/Users/Ken/Desktop/6200/AP_DATA/query_desc.51-100.short.txt"
RESULT_PATH = "/Users/Ken/Desktop/result.txt"

es = Elasticsearch()

def _query() : 
    query_path = QUERY_PATH
    result_path = RESULT_PATH
    query = open(query_path, 'r')
    result = open(result_path, 'w')
    
    for line in query :
        words = line_process(line)
        if len(words) == 0 :
            break

        score_dict = {}

        print words[0]
        for word in words[1:] :
            print word
            file_num = 500
            res = es.search(index = "ap_dataset", doc_type = "document", body = query_body(word), size = file_num)
            avg_len = 247

            for doc in res['hits']['hits'] :
                docno = doc['_source']['docno']
                tf = doc['_score']
                length = len(es.indices.analyze(analyzer='english', body=doc['_source']['text'])['tokens'])
                #length = get_length(doc['_id'])

                okapi_tf = (float(tf)) / (tf + 0.5 + 1.5 * (length / avg_len))

                score = okapi_tf

                if score_dict.has_key(docno) :
                    score_dict[docno] += score
                else :
                    score_dict[docno] = score

        sorted_dic = sorted(score_dict.items(), key=operator.itemgetter(1), reverse = True)

        i = 0
        for key in sorted_dic :
            i += 1
            if i > 100 :
                break
            #print key[0]
            #print key[1]
            line = str(words[0]) + " Q0 " + key[0] + " " + str(i) + " " + str(key[1]) + " Exp\n"
            result.write(line)

    query.close()
    result.close()

def line_process(line) :
    line = line.replace(',', '')
    line = line.replace('.', '')

    tmp = line.split()
    words = line.split() 
    for t in tmp :
        if t in meaningless_word : 
            words.remove(t)

    return words

def query_body (word) :
    ttf =  "_index['text'][" + word + "].ttf()"
    df = "_index['text'][" + word + "].df()"
    _body = {
        "query": {
            "function_score": {
              "query": {
                "match": {
                  "text": word
                }
              },
              "boost_mode":"replace",
              "functions": [
                {
                  "script_score": {
                    "script": "_index['text']['" + word + "'].tf()"
                  }
                }
              ]
            }
          },
          #"_source": "docno",
          "size": 10,
          "facets": {
            "ttf": {
              "statistical": {
                "script": "_index['text']['" + word + "'].ttf()"
              }
            },
            "df": {
              "statistical": {
                "script": "_index['text']['" + word + "'].df()"
              }
            }
          }
        }

    return _body

def get_length(docid) :
    #res = es.termvector(index = "ap_dataset", doc_type = "document", id = docid) 
    #leng = 0
    #token = res['term_vectors']['text']['terms']
    #for i in token.keys():
    #    leng += token[i]['term_freq']

    #return leng

    res = es.search(index = "ap_dataset", doc_type = "document", body = 
        {
            "query": {
                "match": {
                    "docno" : docid
                }
            },
            "facets": {
                "stat1": {
                    "statistical": {
                        "script": "doc['text'].values.size()"
                  }
                }
              }
        })        

    return res["facets"]["stat1"]["total"]



if __name__ == '__main__' : 
    _query()
