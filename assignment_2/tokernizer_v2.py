#!/usr/bin/python 
import os
import re
from stemming.porter2 import stem

COURSE_PATH = "/Users/Ken/Desktop/6200/"
DATA_PATH = COURSE_PATH + "AP_DATA/"
INDEX_PATH = COURSE_PATH + "assignment_2/Index2/"

def read_folder(FOLDER_PATH) : 
    counter = 0
    for file_name in os.listdir(FOLDER_PATH) : 
        with open(FOLDER_PATH + file_name, 'r') as f:
            print file_name
            for each in re.findall(r"<DOCNO> (.*?) </DOCNO>[\s\S]*?<TEXT>\n([\s\S]*?)\n</TEXT>[\s\S].*?", f.read()) :
                tokenize(each[0], re.findall(r"\w+(?:\.?w+)*", each[1]))
        
        counter += 1
        if counter == 1 :  
            break

def tokenize(docno, tokens) :
    global interval
    global term_set
    global index
    global stoplist
    global doc_len

    tmp = 0

    for i in range(len(tokens)) :
        term = stem(tokens[i])
        
        if term in stoplist :
            tmp += 1
            continue
        if  (len(term_set) >= interval and term not in term_set) or (term in term_set and term not in index) :
            continue
        else :
            if term not in term_set :
                index[term] = {}
                term_set.add(term)

            if docno not in index[term] :
                index[term][docno] = []

            index[term][docno].append(i)

    doc_len[docno] = len(tokens) - tmp

def write_result(result_path) :
    offset = open(result_path + 'offset.txt', 'a+')
    index_file = open(result_path + 'index.txt', 'a+')

    global index
    global offset_position

    for term in index :
        tmp = ""
        for doc in index[term] : 
            tmp += doc + " " + " ".join(str(v) for v in index[term][doc]) + ";" 

        index_file.write(tmp)
        offset.write(term + " " + str(offset_position) + " " + str(len(tmp)) + "\n")

        offset_position += len(tmp)

    offset.close()
    index_file.close()

if __name__ == '__main__' :
    gap = 1000
    interval = gap 
    offset_position = 0 

    term_set = set()
    index = {}
    doc_len = {}

    with open(DATA_PATH + "stoplist.txt", 'r') as f :
        stoplist = set(f.read().split())

    while len(index) < interval :
        read_folder(DATA_PATH + "ap89_collection/")
        write_result(INDEX_PATH)
        index.clear()

        if len(term_set) != interval :
            print "break"
            break

        interval += gap

    with open(INDEX_PATH + "doc_len.txt", 'w') as f :
        for i in doc_len.keys() :
            f.write(i + "  " + str(doc_len[i]) + "\n")
