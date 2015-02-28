#!/usr/bin/python
import json
import os
import math
from datetime import datetime
from elasticsearch import Elasticsearch

INDEX_NAME = "ap_dataset"

es = Elasticsearch()

id_num = 1

def read_folder(FOLDER_PATH) : 
	for file_name in os.listdir(FOLDER_PATH) : 
		file_path = FOLDER_PATH + file_name
		print file_name
		read_each_file(file_path)

def read_each_file(file_path) : 
	file = open(file_path, 'r')

	flag = 0
	content = ""

	for line in file:
		if '<DOCNO>' in line :
			docno = line.split(' ')[1]
		elif '<TEXT>' in line :
			flag = 1 
		elif '</TEXT>' in line :
			flag = 0
		elif flag == 1:
			content += str(line)
		elif '</DOC>' in line :
                        global id_num
			index(id_num, docno, content)
			content = ""
                        id_num += 1
	file.close()

def index(id_num, docno, content) :
	es.index(
	    index=INDEX_NAME,
		doc_type="document",
		id = id_num,
		body = {
                        "docno" : docno,
			"text":content
		}
	)

if __name__ == '__main__' :
	
	read_folder("/Users/Ken/Desktop/AP_DATA/ap89_collection/")
