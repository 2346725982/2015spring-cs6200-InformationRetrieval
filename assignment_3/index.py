from elasticsearch import Elasticsearch

es = Elasticsearch()
FOLDER_PATH = '/Users/Ken/Desktop/crawl/'

def readEachFile(i, inlinks):
    global es
    with open(FOLDER_PATH + str(i), 'r') as f:
        content = f.read().split('<next_block_of_content>\n')

        tmp_inlinks = []
        tmp_inlinks.extend(inlinks[content[0].strip()])

        es.index(
            index = 'test',
            doc_type = 'document',
            id = content[0].strip(), 
            body = {
                'docid' : content[0].strip(),
                'text' : content[1],
                'outlinks' : content[2],
                'inlinks' : '\n'.join(tmp_inlinks),
                'html' : content[3]
            }
        )

def main():
    total = 3
    inlinks = {}

    with open(FOLDER_PATH + 'inlinks', 'r') as f:
        for line in f:
            tmp = line.split('    ')
            inlinks[tmp[0]] = tmp[1].split(';')

    for i in range(1, total):
        readEachFile(i, inlinks)

if __name__ == '__main__':
    main()
