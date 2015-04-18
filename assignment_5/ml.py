import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeRegressor

cwd = '/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_5/'
features = ['bm25', 'laplace', 'lm', 'okapi', 'tf_idf']

def main():
    queryid = {}
    docid = {}
    queryid2 = {}
    docid2 = {}

    # Map query and doc with numbers
    with open(cwd + 'query_desc.51-100.short.txt', 'r') as qrel:
        for line in qrel:
            try:
                query = line.split()[0]
                query = query[:len(query)-1]

                if query not in queryid:
                    tmp = len(queryid)
                    queryid[query] = tmp
                    queryid2[tmp] = query
            except:
                pass

    with open(cwd + 'qrels.adhoc.51-100.AP89.txt', 'r') as qrel:
        for line in qrel:
            query, zero, doc, score = line.split()

            if query in queryid and doc not in docid:
                tmp = len(docid)
                docid[doc] = tmp
                docid2[tmp] = doc

    # Read score to label
    N = len(queryid)
    M = len(docid)
    O = len(features)

    label = [0] * (N * M)
    matrix = [[0 for x in range(O)] for x in range(N * M)] 

    with open(cwd + 'qrels.adhoc.51-100.AP89.txt', 'r') as qrel:
        for line in qrel:
            query, zero, doc, score = line.split()

            try:
                row = queryid[query] * M + docid[doc]
                label[row] = int(score)
            except:
                pass

    # Read feature score
    for column in range(len(features)):
        with open(cwd + 'result/' + features[column], 'r') as feature:
            for line in feature:
                query, asseser, doc, rank, score, exp = line.split()

                try:
                    row = queryid[query] * M + docid[doc]
                    matrix[row][column] = float(score)

                except:
                    pass

    # Machine Learning
    x = np.array(matrix[:20*M])
    r = np.array(matrix[20*M:])
    y = np.array(label[:20*M])
    clf = DecisionTreeRegressor()
    #clf = LinearRegression()
    #clf = SVC()
    print 'start learning'
    clf.fit(x, y)
    print 'end learning'

    pre_train = clf.predict(x)
    pre_test = clf.predict(r)

    result = np.append(pre_train, pre_test)

    # Output prediction
    with open(cwd + 'train', 'w') as train, open(cwd + 'test', 'w') as test:
        # Write to train
        dic = {}
        for i in range(20 * M):
            query = queryid2[i / M]
            doc = docid2[i % M]
            score = result[i]

            if query not in dic:
                dic[query] = {}

            dic[query][doc] = score

        for i in dic:
            sorted_dic = sorted(dic[i], key=dic[i].get, reverse=True)
            n = 0
            for key in sorted_dic :
                n += 1
                if n > 1000 :
                    break
                line = i + " Q0 " + str(key) + ' ' + str(n) + " " + str(dic[i][key]) + " Exp\n"
                train.write(line) 

        # Write to test
        dic = {}
        for i in range(20 * M, len(result)):
            query = queryid2[i / M]
            doc = docid2[i % M]
            score = result[i]

            if query not in dic:
                dic[query] = {}

            dic[query][doc] = score

        for i in dic:
            sorted_dic = sorted(dic[i], key=dic[i].get, reverse=True)
            n = 0
            for key in sorted_dic :
                n += 1
                if n > 100 :
                    break
                line = i + " Q0 " + str(key) + ' ' + str(n) + " " + str(dic[i][key]) + " Exp\n"
                test.write(line) 

if __name__ == '__main__':
    main()
