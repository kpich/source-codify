#!/usr/bin/env python

import sys

def main(file1, file2, file3):
    anns1 = read_annotation_map(file1)
    anns2 = read_annotation_map(file2)
    anns3 = read_annotation_map(file3)
    overlap12 = get_key_overlap(anns1, anns2)
    disagreement12 = get_disagreements(anns1, anns2)
    overlap13 = get_key_overlap(anns1, anns3)
    disagreement13 = get_disagreements(anns1, anns3)
    overlap23 = get_key_overlap(anns2, anns3)
    disagreement23 = get_disagreements(anns2, anns3)
    print 'overlap between 1 and 2: %d' %  len(overlap12)
    print 'Agreement between 1 and 2: %f' % (float(len(overlap12) - len(disagreement12)) / len(overlap12))
    print 'overlap between 1 and 3: %d' %  len(overlap13)
    print 'Agreement between 1 and 3: %f' % (float(len(overlap13) - len(disagreement13)) / len(overlap13))
    print 'overlap between 2 and 3: %d' %  len(overlap23)
    print 'Agreement between 2 and 3: %f' % (float(len(overlap23) - len(disagreement23)) / len(overlap23))
    diskeys1 = [x[1] for x in disagreement12]
    diskeys2 = [x[1] for x in disagreement13]
    diskeys3 = [x[1] for x in disagreement23]
    print '========================'
    print sorted(diskeys1)
    print '========================'
    print sorted(diskeys2)
    print '========================'
    print sorted(diskeys3)
    print '========================'
    print '========================'
    print '========================'
    labs = set(anns1.values())
    print '1'
    for lab in labs: print '\t%s: %d' % (lab, anns1.values().count(lab))
    print '2'
    for lab in labs: print '\t%s: %d' % (lab, anns2.values().count(lab))
    print '3'
    for lab in labs: print '\t%s: %d' % (lab, anns3.values().count(lab))

def get_key_overlap(map1, map2):
    return [k for k,v in map1.items() if k in map2]

def get_disagreements(map1, map2):
    return [(k,v) for k,v in map1.items() if k in map2 and map2[k] != v]
        
def read_annotation_map(filename):
    d = dict()
    for line in open(filename, 'r'):
        toks = line.split()
        if len(toks) == 2:
            d[toks[0]] = toks[1]
    return d

if __name__ == '__main__':
    main(*sys.argv[1:])
