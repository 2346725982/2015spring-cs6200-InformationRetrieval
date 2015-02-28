#!/usr/bin/python 
import math
import time
import os
import sys
import re
from stemming.porter2 import stem

def get_stopword(path) :
    stopwords = []
    file = open(path, 'r')
    
    for line in file :
        stopwords.append(line.strip())

    file.close()

    return stopwords

def read_folder(FOLDER_PATH) : 
    global counter

    for file_name in os.listdir(FOLDER_PATH) : 
	file_path = FOLDER_PATH + file_name
	print file_name
	read_each_file(file_path)
        
        #counter += 1
        #if counter == 1 : 
        #    break

def read_each_file(file_path) : 
    file = open(file_path, 'r')
    
    global possition
    global stopwords_num
    global doc_len
    
    flag = 0
    content = ""

    for line in file:
        if '<DOCNO>' in line :
            docno = line.split(' ')[1]
            possition = 0
            stopwords_num = 0
        elif '<TEXT>' in line :
            flag = 1 
        elif '</TEXT>' in line :
            flag = 0
        elif flag == 1:
            content += str(line)
        elif '</DOC>' in line :
            tokenize(docno, content)
            content = ""
            doc_len[docno] = possition - stopwords_num
    file.close()

def tokenize(docno, content) :
    content = content.replace('``', '')
    content = content.replace('`', '')
    content = content.replace('\'\'', '')
    content = content.replace(',', '')
    content = content.replace('.', '')
    content = content.replace('!', '')
    content = content.replace('?', '')
    content = content.replace(';', '')
    content = content.replace('_', '')
    content = content.replace('{', '')
    content = content.replace('}', '')
    content = content.replace('(', ' ')
    content = content.replace(')', ' ')
    content = content.lower()

    content_words = content.split()
    global id_map
    global id_map2
    global tokenizer
    global word_index
    global interval
    global possition
    global stopwords_num

    for word in content_words :
        possition += 1

        word = stem(word)

        if len(word) == 1 or word in stopwords :
            stopwords_num += 1
            continue

        if word in id_map and id_map[word] not in tokenizer :
            continue
        elif word in id_map and docno in tokenizer[id_map[word]] :
            tokenizer[id_map[word]][docno].append(possition)
        elif word in id_map and docno not in tokenizer[id_map[word]] :
            tokenizer[id_map[word]][docno] = [possition]
        elif word_index < interval :
            id_map[word] = word_index 
            id_map2[word_index] = word
            term_possition = {docno : [possition]}
            tokenizer[word_index] = term_possition
            #print tokenizer[word_index]
            word_index += 1
        else :
            continue

def write_result(path) :
    offset = open(path + 'offset.txt', 'a+')
    index = open(path + 'index.txt', 'a+')

    global id_map2
    global tokenizer
    global offset_position
    global interval
    global gap

    for i in tokenizer.keys() :
        #tmp_offset = offset_position
        tmp = str(id_map2[i]) + ";"
        #offset_position += 1
        for j in tokenizer[i].keys() :
            tmp += str(j) + "," + str(len(tokenizer[i][j])) + ":"
            for k in tokenizer[i][j] : 
                tmp += str(k) + " "
            tmp += ";"

        index.write(tmp)

        offset.write(id_map2[i] + " " + str(offset_position + len(id_map2[i]) + 1))
        offset.write( " " + str(len(tmp) - len(id_map2[i]) - 1) + "\n")
        offset_position += len(tmp)
        
        #print tmp

        #find = re.findall(r"(.*?),(.*?):(.*);", tmp)


    #print len(tokenizer)
    print "done"
    offset.close()
    index.close()

def write_dlen(path) :
    dlen = open(path, 'w')

    global doc_len
    global total_dlen

    for i in doc_len.keys() :
        dlen.write(i + "  " + str(doc_len[i]) + "\n")
        total_dlen += doc_len[i]

    dlen.close()

if __name__ == '__main__' :
    id_map = {}
    id_map2 = {}
    doc_len = {}
    tokenizer = {}
    total_dlen = 0
    word_index = 1
    gap = 50000
    interval = gap
    offset_position = 0
    possition = 0
    stopwords_num = 0

    stopwords = get_stopword("/Users/Ken/Desktop/6200/AP_DATA/stoplist.txt")

    t = time.time()
    while word_index < interval :
        counter = 0
        read_folder("/Users/Ken/Desktop/6200/AP_DATA/ap89_collection/")
        write_result("/Users/Ken/Desktop/6200/assignment_2/Index/")

        tokenizer.clear()

        #if word_index == 3000 : 
        if word_index != interval :
            print "break"
            break

        interval += gap
        print word_index

    print time.time() - t

    write_dlen("/Users/Ken/Desktop/6200/assignment_2/Index/doc_len.txt")

    print "total document number: " + str(len(doc_len))
    print "average document length: " + str(total_dlen / len(doc_len))
    print "vocabylary size: " + str(word_index - 1)
