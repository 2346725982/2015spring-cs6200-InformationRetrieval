#!/usr/bin/python

"""
QueryID AssessorID DocID Grade

QueryID AssessorID Number DocID Grade
"""

def main():
    path = '/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_4/'
    entry = []
    with open(path + '150301 Hurricane Sandy.txt', 'r') as query1, \
         open(path + '150302 hurricane katrina damage.txt', 'r') as query2, \
         open(path + '150303 hurricane Ike.txt', 'r') as query3:
             for line in query1.read().split('\n'):
                 i = line.split()
                 entry.append([150301, 'Z_Wang', int(i[0]), i[2], int(i[1])])

             for line in query2.read().split('\n'):
                 i = line.split()
                 entry.append([150302, 'Z_Wang', int(i[0]), i[2], int(i[1])])

             for line in query3.read().split('\n'):
                 i = line.split()
                 entry.append([150303, 'Z_Wang', int(i[0]), i[2], int(i[1])])

    with open(path + 'QREL', 'w') as qrel:
        for i in range(len(entry)):
            l = []
            l.append(str(entry[i][0]))
            l.append(entry[i][1])
            l.append(entry[i][3])
            l.append(str(entry[i][4]))
            l.append('\n')

            qrel.write(' '.join(l))

    return

if __name__ == '__main__':
    main()
