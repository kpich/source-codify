#!/usr/bin/env python
''' Takes the following:
    - A file containing the repo names whose files we are going to copy, one
      per line.
    - The directory containing one file per repo (with the files named after
      the repos), each of which contains the paths to the *.java files.
    - a base directory containing the files pointed to in the second param
    - the destination directory of the resultant files.

    outputs a mirrored directory structure, but with stemmed files, in the 
    second argument.
'''

import os
import stemmer
import sys

def main(repolist_fname, repo_flist_dirname, src_dir, dest_dir):
    for reponame in open(repolist_fname, 'r'):
        reponame = reponame.strip()
        fnames = get_fnames(reponame, repo_flist_dirname)
        print 'stemming files for %s...' % reponame
        stem_files(fnames, src_dir, dest_dir)

def stem_files(fnames, src_dir, dest_dir):
    p = stemmer.PorterStemmer()
    for fname in fnames:
        srcname = os.path.join(src_dir, fname)
        destname = os.path.join(dest_dir, fname)
        ensure_dir(destname)
        f = open(destname, 'w')
        for tok in get_raw_tokens(srcname):
            f.write('%s\n' % p.stem(tok, 0, len(tok) - 1))
        f.close()

def get_raw_tokens(srcname):
    lines = open(srcname, 'r').readlines()
    for line in lines:
        for tok in line.split():
            if len(tok) > 0:
                yield tok

def get_fnames(reponame, repo_flist_dirname):
    return [x.strip() for x in
            open(os.path.join(repo_flist_dirname, reponame), 'r').readlines()]

def ensure_dir(filename):
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        os.makedirs(d)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.stderr.write('wrong num args!\n')
        sys.exit()
    main(*sys.argv[1:])
