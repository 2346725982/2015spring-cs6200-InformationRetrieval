def convert(l, pageid):
    row = []
    for i in l:
        if i not in pageid:
            index = len(pageid)
            pageid[i] = index

        row.append(pageid[i])
    return row

def generateNew(pageid, links, outlinks, old):
    new = [0.15 / N] * N
    for i in range(len(links)):
        for j in range(1, len(links[i])):
            page = links[i][j]

            new[i] += 0.85 * old[pageid[page]] / outlinks[page]

    return new

if __name__ == '__main__':
    links = []
    outlinks = {}
    pageid = {}

    with open('/Users/Ken/Documents/2015spring-cs6200-InformationRetrieval/assignment_4/wt2g_inlinks.txt', 'r') as f:
        for line in f:
            #l = convert(line.split(), pageid)
            l = line.split()
            links.append(l)

            pageid[l[0]] = len(pageid)

            for i in range(1, len(l)):
                if l[i] not in outlinks:
                    outlinks[l[i]] = 0
                outlinks[l[i]] += 1

    N = len(links)
    done = False

    old = [float(1) / N] * N
    new = [0] * N

    #it = 0
    while not done:
        #it += 1
        #print it
        new = generateNew(pageid, links, outlinks, old)

        tmp = [a - b for a, b in zip(new, old)]
        tmp = [i * i for i in tmp]
        tmp = sum(tmp)
        tmp = tmp ** 0.5 / N

        done = (tmp < 10 ** -16)

        old = new
        new = [0] * N

    result = {}

    for i in pageid:
        result[i] = old[pageid[i]]

    sorted_x = sorted(result.items(), key=lambda x: x[1])

    for i in sorted_x:
        print i
