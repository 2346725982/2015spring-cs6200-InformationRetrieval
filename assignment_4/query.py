#! /usr/bin/python

import math
import time
import operator
from elasticsearch import Elasticsearch

meaningless_word = {"Document", "will", "or", "a", "of", "the", "on", "something", "by", "about", "with", "as", "to", "over", "either", "which", "in", "how", "and", "identify", "one", "discuss", "report", "include", "some", "an", "any", "has", "at", "must", "being", "against", "into", "its", "used", "certain", "US","\"dual-use\"", "even", "other", "been", "doing", "since", "use", "both" }

es = Elasticsearch()


def _query() :
    query_path = "/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_4/query2.txt"
    result_path = "/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_4/TF_IDF"

    source = open(query_path, 'r')
    target = open(result_path, "w")

    for line in source :
        starttime = time.time()
        words = line_process(line)
        if len(words) == 0 :
            break

        score_dict = {}
        starttime = time.time()
        for word in words[1:] :
            update_score(word, score_dict)
        endtime = time.time()
        print "word: ", str(endtime - starttime), " s"

        write_result(target, words[0], score_dict)
        endtime = time.time()
        print "for query : \"", line, "\""
        print "it takes " + str(endtime - starttime) + " s"
    target.close()
    source.close()

def query_body (word) :
    _body = {
        "query" : {
            "match" : {
                "text" : word
            }
	}
    }
    return _body

def facets_body() :
    _body = {
        "facets" : {
            "stat1" : {
                "statistical" : {
                    "script" : "doc['text'].values.size()"
                }
            }
        }
    }
    return _body

def line_process(line) :
    line = line.replace(',', '')
    line = line.replace('.', '')

    tmp = line.split()
    words = line.split()
    for t in tmp :
        if t in meaningless_word :
            words.remove(t)

    return words

def update_score(word, score_dict) :
    file_num = 100
    starttime = time.time()
    res = es.search(index = "ap_dataset", doc_type = "document", body = query_body(word), size = file_num)
    endtime = time.time()
    print "search time: ", str(endtime - starttime), " s"

    tf_dic = {}
    len_dic = {}

    D = 84680
    df = get_df(res)
    idf = float(D) / df
    t_tf = 0

    starttime = time.time()
    for doc in res["hits"]["hits"] :
        print 'in loop'
        docid = doc["_source"]["docno"]
        _id = doc["_id"]
        tf = get_tf(_id, word)
        leng = get_len(docid)
        t_tf += tf

        tf_dic[docid] = tf
        len_dic[docid] = leng

    endtime = time.time()
    print word, ", all docs: ", str(endtime - starttime), " s"
    #Okapi_TF_Model(tf_dic, idf, len_dic, avg_len, score_dict)
    TF_IDF_Model(tf_dic, idf, len_dic, avg_len, score_dict)
    #Okapi_BM25_Model(tf_dic, len_dic, avg_len, D, df, score_dict)
    #Unigram_LM_Laplace_smoothing_Model(tf_dic, len_dic, score_dict)
    #Unigram_LM_JM_smoothing_Model(tf_dic, len_dic, score_dict, t_tf)

def get_df(res) :
    return res["hits"]["total"]

def get_avg_len() :
    res = es.search(index = "ap_dataset", doc_type = "document",
    body = {
        "query" : {
            "match_all":{}
        },
        "facets" : {
            "stat1" : {
                "statistical" : {
                    "script" : "doc['text'].values.size()"
                }
            }
        }
    })

    return res["facets"]["stat1"]["mean"]

def get_tf(docid, word) :
    res = es.explain(index = "ap_dataset", doc_type = "document", id = docid, body = query_body(word))

    res = res["explanation"]["details"][0]["details"]

    if '-' in word :
        res = res[0]["details"]
    if len(res) < 2 :
        res = res[0]["details"]
    if len(res) < 3 :
        res = res[1]["details"]

    return res[0]["details"][0]["value"]

def get_len(docid) :
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

def sortedDic(adict):
    items = adict.items()
    items.sort()
    return [value  for key, value  in items]

def write_result(target, query_num, score_dict) :
    sorted_dic = sorted(score_dict.items(), key=operator.itemgetter(1), reverse = True)
    i = 0
    for key in sorted_dic :
        i += 1
        if i > 1000 :
            break
        line = str(query_num) + " Q0 " + key[0] + " " + str(i) + " " + str(key[1]) + " Exp\n"
        target.write(line)

## 5 Models ##

def Okapi_TF_Model(tf_dic, idf, len_dic, avg_len, score_dic) :
    for i in tf_dic :
        if score_dic.has_key(i) :
            score_dic[i] += Okapi_TF(tf_dic[i], len_dic[i], avg_len)
        else :
            score_dic[i] = Okapi_TF(tf_dic[i], len_dic[i], avg_len)

def Okapi_TF(tf, leng, avg_len) :
    return (float(tf)) / (tf + 0.5 + 1.5 * (leng / avg_len))

def TF_IDF_Model(tf_dic, idf, len_dic, avg_len, score_dic) :
    for i in tf_dic :
        if score_dic.has_key(i) :
            score_dic[i] += Okapi_TF(tf_dic[i], len_dic[i], avg_len) * math.log(idf)
        else :
            score_dic[i] = Okapi_TF(tf_dic[i], len_dic[i], avg_len) * math.log(idf)

def Okapi_BM25_Model(tf_dic, len_dic, avg_len, D, df, score_dic) :
    for i in tf_dic :
        if score_dic.has_key(i) :
            score_dic[i] += Okapi_BM25(tf_dic[i], len_dic[i], avg_len, D, df)
        else :
            score_dic[i] = Okapi_BM25(tf_dic[i], len_dic[i], avg_len, D, df)

def Okapi_BM25(tf, d_len, avg_len, D, df) :
    k1 = 1.2
    k2 = 500
    b = 0.75

    n1 = math.log(float(D + 0.5) / (df + 0.5))
    n2 = (tf + k1 * tf) / (tf + k1 * ((1 - b) + b * (d_len / avg_len)))
    n3 = (tf + k2 * tf) / (tf + k2)
    bm = n1 * n2 * n3
    return bm

def Unigram_LM_Laplace_smoothing_Model(tf_dic, len_dic, score_dic) :
    for i in tf_dic :
    	if score_dic.has_key(i) :
	    score_dic[i] += Unigram_LM_Laplace(tf_dic[i], len_dic[i])
        else :
            score_dic[i] = Unigram_LM_Laplace(tf_dic[i], len_dic[i])

def Unigram_LM_Laplace(tf, leng) :
    V = 178050
    p_laplace = ((tf + 1) / (float(leng + V)))
    lm_laplace = math.log(p_laplace)

    return lm_laplace

def Unigram_LM_JM_smoothing_Model(tf_dic, len_dic, score_dic, t_tf) :
    for i in tf_dic :
    	if score_dic.has_key(i) :
	    score_dic[i] += Unigram_LM_JM(tf_dic[i], len_dic[i], t_tf)
        else :
            score_dic[i] = Unigram_LM_JM(tf_dic[i], len_dic[i], t_tf)

def Unigram_LM_JM(tf, leng, t_tf) :
    td = 13950891
    ttf = t_tf
    lamb = 0.1
    p_jm = lamb * (float(tf) / leng) + (1 - lamb) * (float(ttf - tf) / (td - leng))
    lm_jm = math.log(p_jm)

    return lm_jm

## main function ##
if __name__ == "__main__" :
    avg_len = 247#get_avg_len()
    _query()
    #get_len("AP891216-0051")


