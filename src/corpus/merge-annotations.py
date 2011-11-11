#!/usr/bin/env python
''' This is the script that compiles the final corpus. It takes:
    - the three initial annotation files from annotators A, B, C
    - the three adjudication annotation files from annotators A, B, C in the
      same order (so if the first three params are A, B, C, the fourth param
      is the adjudicated disagreements between B&C, the fifth is the ones
      between A&C, and the last is the disagreements between A&B).
'''

import os
import sys

def main(file1, file2, file3,
         resolve23, resolve13, resolve12):
    anns1 = read_annotation_map(file1)
    anns2 = read_annotation_map(file2)
    anns3 = read_annotation_map(file3)
    resolutions23 = read_annotation_map(resolve23)
    resolutions13 = read_annotation_map(resolve13)
    resolutions12 = read_annotation_map(resolve12)
    final_labels = construct_final_anns(anns1, anns2, anns3,
                                        resolutions23, resolutions13, resolutions12)
    labs = set(anns1.values() + anns2.values() + anns3.values())
    for url,lab in final_labels.items():
        print '%s\t%s' % (url, lab)

def construct_final_anns(anns1, anns2, anns3, resolutions23, resolutions13, resolutions12):
    res = dict()
    o12 = get_key_overlap(anns1, anns2)
    o13 = get_key_overlap(anns1, anns3)
    o23 = get_key_overlap(anns2, anns3)
    d12 = get_disagreements(anns1, anns2)
    d13 = get_disagreements(anns1, anns3)
    d23 = get_disagreements(anns2, anns3)

    for good_key in set(o12) - set(d12):
        res[good_key] = anns1[good_key]
    for good_key in set(o13) - set(d13):
        res[good_key] = anns1[good_key]
    for good_key in set(o23) - set(d23):
        res[good_key] = anns2[good_key]

    for bad_key in d12:
        if resolutions12[bad_key] == anns1[bad_key] or \
           resolutions12[bad_key] == anns2[bad_key]:
            res[bad_key] = resolutions12[bad_key]
        else:
            sys.stderr.write('disagreement between 1 and 2: %s\n' % bad_key)
            sys.stderr.write('\t1: %s\n' % anns1[bad_key])
            sys.stderr.write('\t2: %s\n' % anns2[bad_key])
            res[bad_key] = 'other'
    for bad_key in d13:
        if resolutions13[bad_key] == anns1[bad_key] or \
           resolutions13[bad_key] == anns3[bad_key]:
            res[bad_key] = resolutions13[bad_key]
        else:
            sys.stderr.write('disagreement between 1 and 3: %s\n' % bad_key)
            sys.stderr.write('\t1: %s\n' % anns1[bad_key])
            sys.stderr.write('\t3: %s\n' % anns3[bad_key])
            res[bad_key] = 'other'
    for bad_key in d23:
        if resolutions23[bad_key] == anns2[bad_key] or \
           resolutions23[bad_key] == anns3[bad_key]:
            res[bad_key] = resolutions23[bad_key]
        else:
            sys.stderr.write('disagreement between 2 and 3: %s\n' % bad_key)
            sys.stderr.write('\t2: %s\n' % anns2[bad_key])
            sys.stderr.write('\t3: %s\n' % anns3[bad_key])
            res[bad_key] = 'other'
    return res

def get_key_overlap(map1, map2):
    return [k for k,v in map1.items() if k in map2]

def get_disagreements(map1, map2):
    return [k for k,v in map1.items() if k in map2 and map2[k] != v]
        
def read_annotation_map(filename):
    d = dict()
    for line in open(filename, 'r'):
        toks = line.split()
        assert len(toks) != 1
        if len(toks) == 2:
            d[toks[0]] = toks[1]
    return d

if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.stderr.write("wrong line of args! see comments in script\n")
        sys.exit()
    main(*sys.argv[1:])
