#!/usr/bin/env python

import itertools
import random
import sys

N = 10

def main(fname):
    sets = partition_lines(fname)
    for fold in range(N):
        f = open('%s.test.%d' % (fname, fold), 'w')
        for li in sets[fold]:
            f.write('%s\n' % li)
        f.close()
        f = open('%s.train.%d' % (fname, fold), 'w')
        # for every line in every set that isn't at fold:
        for li in itertools.chain(*(sets[:fold] + sets[(fold+1):])):
            f.write('%s\n' % li)
        f.close()

def partition_lines(fname):
    lines = [x.strip() for x in open(fname, 'r').readlines()]
    partsize = len(lines) / N
    res = []
    for i in range(N - 1):
        res.append([])
        for j in range(partsize):
            res[i].append(lines.pop(random.randint(0, len(lines) - 1)))
    res.append(lines)
    return res

if __name__ == '__main__':
    main(sys.argv[1])
