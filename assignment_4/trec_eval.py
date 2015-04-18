#!/usr/bin/python
import sys
from math import log
#import pylab as pl
#from sklearn import svm, datasets
#from sklearn.metrics import precision_recall_curve
#from sklearn.metrics import auc

"""
R-precision, Average Precision, nDCG, precision@k and recall@k
and F1@k (k=5,10, 20, 50, 100). Average these numbers over the queryIDs
"""


def main():
    """
    read arguments from system
    """
    qrel_path = sys.argv[1]
    result_path = sys.argv[2]

    if len(sys.argv) == 4:
        print 'q option'
        sys.argv[4] == '-q'

    """
    read QREL file
    """
    qrel = {}
    relevant = {}

    with open(qrel_path, 'r') as f:
        for line in f.read().split('\n'):
            query, assessor, docid, score = line.strip().split()

            if query not in qrel:
                qrel[query] = {}

            qrel[query][docid] = score

    for each in qrel:
        count = len([i for i in qrel[each] if qrel[each][i] != '0'])
        relevant[each] = count

    """
    read RESULT file, deal with it
    """
    confusion = {}
    result = {}
    nDCG = {}

    with open(result_path, 'r') as f:
        for line in f.read().split('\n'):
            query, qZero, docid, rank, score, Exp = line.split()

            rank = int(rank)

            # initialization
            if query not in confusion:
                # tp, fp, fn
                confusion[query] = {0: [0, 0, relevant[query]]}
                # precision@k and recall@k and F1@k
                result[query] = {0: [0, 0, 0]}

                # nDCG
                nDCG[query] = []

            # update tp, fp, fn from above entry
            # update nDCG
            last_confusion = confusion[query][rank-1]
            if docid not in qrel[query] or qrel[query][docid] == '0':
                last_confusion[1] += 1
                nDCG[query].append(0)
            else:
                last_confusion[0] += 1
                last_confusion[2] -= 1
                nDCG[query].append(int(qrel[query][docid]))

            confusion[query][rank] = last_confusion

            # calculate precision, recall and F1
            tp, fp, fn = last_confusion
            precision = float(tp) / (tp + fp)
            recall = float(tp) / (tp + fn)
            f1 = (0
                  if precision == 0 or recall == 0
                  else 2 * precision * recall / (precision + recall))

            result[query][rank] = (precision, recall, f1)

        # calculate nDCG
        for i in nDCG:
            DCG = nDCG[i]
            iDCG = sorted(nDCG[i], reverse=True)

            n1 = 0
            n2 = 0
            for j in range(len(DCG)):
                n1 += (DCG[j]
                       if log(j + 1) == 0
                       else DCG[j] / log(j + 1))
                n2 += (iDCG[j]
                       if log(j + 1) == 0
                       else iDCG[j] / log(j + 1))

            n3 = (0
                  if n2 == 0 or n1 == 0
                  else n1 / n2)
            #print 'query', i, 'nDCG', n3

        # calculate average precision
        avg_precision = []
        for i in result:
            average_precision = 0
            for j in range(1, len(result[i])):
                average_precision += result[i][j][0] * (result[i][j][1] - result[i][j-1][1])
            #print 'query', i, 'average_precision', average_precision / (len(result[i]) - 1)
            print 'query', i, 'average_precision', average_precision
            #avg_precision.append(average_precision / (len(result[i]) - 1))
            avg_precision.append(average_precision)

        print sum(avg_precision) / len(avg_precision)

        r_precision = []
        for i in result:
            cutoff = relevant[i]
            if cutoff > len(result[i]) - 1:
                #cutoff = confusion[i][len(confusion) - 1][0]
                cutoff = len(confusion[i]) - 1
            r_precision.append(result[i][cutoff][1])
            #print 'query', i, 'R-precision', result[i][cutoff][1]

        print sum(r_precision) / len(r_precision)

        # output precision, recall and F1
        #for i in result:
        #    for j in result[i]:
        #        print 'query', i, 'rank', j, 'precision, recall, f1', result[i][j]

        #plotPrecisionRecallCurve(result)
    return

def plotPrecisionRecallCurve(result):
    global recallDict
    global precisionDict

    recall = []
    precision = []

    for k in result['99']:
        recall.append(result['99'][k][1])

    for k in result['99']:
        precision.append(result['99'][k][0])

    area = auc(recall, precision)

    pl.clf()
    pl.plot(recall, precision, label="Precision-Recall Curve")
    pl.xlabel('Recall')
    pl.ylabel('Precision')
    pl.xlim([0.0, 1.0])
    pl.ylim([0.0, 1.0])
    pl.legend(loc="lower left")
    pl.show()

if __name__ == '__main__':
    main()
