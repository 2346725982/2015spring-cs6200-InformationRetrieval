PATH = '/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_4/'

dic = {}

for i in range(1, 4):
    with open(PATH + 'QREL_' + str(i), 'r') as f:
        for line in f:
            query, asseser, docid, score = line.split()
            if query not in dic:
                dic[query] = {}

            if docid not in dic[query]:
                dic[query][docid] = 0

            dic[query][docid] += int(score)

with open(PATH + 'QREL', 'w') as f:
    for i in dic:
        for j in dic[i]:
            w = []
            w.append(i)
            w.append('0')
            w.append(j)
            w.append(str(int(round(dic[i][j] / 3.0))))
            w.append('\n')
            f.write(' '.join(w))
