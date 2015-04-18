#! /usr/bin/python

import math
import time
import re
import stemming
import operator
from stemming.porter2 import stem

COURSE_PATH = "/Users/Ken/Desktop/6200/"
QUERY_PATH = COURSE_PATH + "AP_DATA/query_desc.51-100.short.txt"
RESULT_PATH = COURSE_PATH + "assignment_2/result/laplace.txt"
INDEX_PATH = COURSE_PATH + "assignment_2/Index2/"

meaningless_word = set(["Document", "will", "or", "a", "of", "the", "on", "something", "by", "about", "with", "as", "to", "over", "either", "which", "in", "how", "and", "one", "discuss", "report", "include", "some", "an", "any", "has", "at", "must", "being", "against", "into", "its", "used", "certain", "US", "even", "other", "been", "doing", "since", "use", "both"])

def _query() : 

    index_path = INDEX_PATH + "index.txt"
    source = open(QUERY_PATH, 'r')
    result = open(RESULT_PATH, "w")
    index = open(index_path, 'r')

    global total_docnum
    global v_size
    global avg_len

    total_len = 0

    offset = {}
    doc_len = {}
    score_dict = {} 

    with open(INDEX_PATH + "offset.txt", 'r') as o :
        for l in o :
            l = l.split()
            offset[l[0]] = (int(l[1]), int(l[2])) 

    with open(INDEX_PATH + "doc_len.txt", 'r') as d :
        for l in d :
            l = l.split()
            doc_len[l[0]] = float(l[1])
            total_len += float(l[1])

    avg_len = total_len / len(doc_len)
    
    for line in source :
        if not line :
            break

        print line

        l = line.replace(',', '').replace('.', '').split()
        words = [x for x in l if x not in meaningless_word]

        score_dict.clear()

        for word in words[1:] :
            if stem(word) not in offset :
                continue

            word = stem(word)

            index.seek(offset[word][0])
            d_block = index.read(offset[word][1]-1)

            for each in d_block.split(';'):
                doc = each.split()[0]
                score_dict[doc] = (len(words) - 1) * math.log(1 / (doc_len[doc] + v_size))

        for word in words[1:] :
            if stem(word) not in offset :
                continue

            tfq = line.split().count(word)
            word = stem(word)

            index.seek(offset[word][0])
            data = index.read(offset[word][1]-1)

            data2 = data.split(';')
            find = sorted(data2, key = lambda x: len(x.split()), reverse = True)
            for i in range(len(data2)):
                doc = data2[i].split()[0]
                tf = len(data2[i].split()) - 1
                
                #TF-IDF
                #tmp1 = (float(tf) / (tf + 0.5 + 1.5 * (float(doc_len[doc]) / avg_len))) 
                #tmp2 = math.log(float(total_docnum) / len(find))
                #score = tmp1 * tmp2

                #BM25
                #tmp1 = math.log((84678 + 0.5) / (len(find) + 0.5))
                #tmp2 = (tf + 1.2 * tf) / (tf + 1.2 * ((1 - 0.75) + 0.75 * (doc_len[doc] / 245)))
                #tmp3 = (tfq + 100 * tfq) / (tfq + 100)
                #score = tmp1 * tmp2 * tmp3
                #if doc not in score_dict :
                #    score_dict[doc] = 0 

                #laplace
                score = math.log((tf + 1) / (doc_len[doc] + 153130)) - math.log(1 / (doc_len[doc] + 153130))

                score_dict[doc] += score

        sorted_dic = sorted(score_dict.items(), key=operator.itemgetter(1), reverse = True)
        for i in range(len(sorted_dic)) :#range(min(len(sorted_dic), 1001)):
            buf = str(words[0]) + " Q0 " + sorted_dic[i][0] + " " 
            buf += str(i) + " " + str(sorted_dic[i][1]) + " Exp\n"
            result.write(buf)

    result.close()
    source.close()
    index.close()

if __name__ == "__main__" : 
    total_docnum = 84678
    avg_len = 245 #426
    v_size = 153130
    _query()
