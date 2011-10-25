#!/usr/bin/env python

import sys

def main(file1, file2, file3):
    anns1 = read_annotation_map(file1)
    anns2 = read_annotation_map(file2)
    anns3 = read_annotation_map(file3)
    overlap12 = get_key_overlap(anns1, anns2)
    disagreement12 = get_disagreements(anns1, anns2)
    print 'overlap between 1 and 2: %d' %  len(overlap12)
    print 'Agreement between 1 and 2: %f' % (float(len(overlap12) - len(disagreement12)) / len(overlap12))

def get_key_overlap(map1, map2):
    return [k for k,v in map1.items() if k in map2]

def get_disagreements(map1, map2):
    return [k for k,v in map1.items() if k in map2 and map2[k] != v]
        
def read_annotation_map(filename):
    d = dict()
    for line in open(filename, 'r'):
        toks = line.split()
        if len(toks) == 2:
            d[toks[0]] = toks[1]
    return d

if __name__ == '__main__':
    main(*sys.argv[1:])
