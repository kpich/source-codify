#!/usr/bin/env python

import gzip
import os
import sys

def main(repo_dirname):
    f = gzip.open(repo_dirname + '.gz', 'wb')
    for dirpath, dirnames, fnames in os.walk(repo_dirname):
        for fname in fnames:
            add_file_to_gz(f, os.path.join(dirpath, fname))
    f.close()

def add_file_to_gz(f, fname):
    f.write('=!=!= %s =!=!=\n' % fname)
    thisf = open(fname, 'r')
    for li in thisf:
        f.write(li)
    thisf.close()

if __name__ == '__main__':
    main(sys.argv[1])
