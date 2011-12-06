#!/usr/bin/env python

import re
import sys

def main(out_fnames):
    tot = 0.0
    for fname in out_fnames:
        firstline = open(fname, 'r').readlines()[0]
        m = re.match(r'Accuracy = ([0-9\.]+)%', firstline)
        tot += float(m.group(1))
    print 'avg acc: %f' % (tot / len(out_fnames))

if __name__ == '__main__':
    main(sys.argv[1:])
