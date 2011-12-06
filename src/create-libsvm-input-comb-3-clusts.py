#!/usr/bin/env python
''' Call with params:
    - a file giving the labels of repos (newline delimited, each line
      containing a "repo-name   label" pair)
    - three filename containing the clusters (as output by the divisive clustering script),
      for features A, B, and C
    - an arbitrary number of gzipped files divisible by 3, each of which contains
      the newline-delimited tokenized repo (with delimiters between files).
      All of the files for features A must occur before all the fiels for features B, which
      must occur before those for C. Further, the feature A files must occur in the same order 
      (and be the same) as the feature B files (ditto feature C).

      so it'll be something like
      ./create-libsvm-input-comb-clusts.py lab-file clustA clustB clustC repo1.A.tok.gz repo2.A.tok.gz repo1.B.tok.gz repo2.B.tok.gz repo1.C.tok.gz repo2.C.tok.gz
'''

import gzip
import itertools
import os
import re
import sys

def main(labelfilename, clustfnameA, clustfnameB, clustfnameC, *repofnames):
    clustsA = read_clusters(clustfnameA)
    clustsB = read_clusters(clustfnameB)
    clustsC = read_clusters(clustfnameC)
    repo_to_lab_map = get_repo_to_lab_map(labelfilename)
    lab_to_num_map = construct_lab_to_num_map(set(repo_to_lab_map.values()))

    fnamesA = repofnames[:(len(repofnames)/3)]
    fnamesB = repofnames[(len(repofnames)/3):(2 * len(repofnames)/3)]
    fnamesC = repofnames[(2 * len(repofnames)/3):]
    assert len(fnamesA) == len(fnamesB)
    assert len(fnamesA) == len(fnamesC)

    for fnameA, fnameB, fnameC in zip(fnamesA, fnamesB, fnamesC):
        reponame1 = os.path.basename(fnameA).replace('.gz', '')
        reponame2 = os.path.basename(fnameB).replace('.gz', '')
        reponame3 = os.path.basename(fnameC).replace('.gz', '')
        assert reponame1 == reponame2
        assert reponame1 == reponame3
        lab = repo_to_lab_map[reponame1]
        sys.stderr.write('extracting features from %s...\n' % reponame1)
        print construct_libsvm_line(lab_to_num_map[lab], fnameA, fnameB, fnameC, clustsA, clustsB, clustsC)

        #try:
        #    print construct_libsvm_line(lab_to_num_map[lab], fnameA, fnameB, clustsA, clsuts)
        #except:
        #    sys.stderr.write('error with repo: %s\n' % reponame1)
            #raise
    for lab,num in lab_to_num_map.items():
        sys.stderr.write('num: %d\tlabel: %s\n' % (num, lab))

def construct_libsvm_line(labelnum, fnameA, fnameB, fnameC, clustsA, clustsB, clustsC):
    ''' constructs features in same order as param 'clusters'.
    '''
    featvalsA = get_feat_vals_from_repo(gzip.open(fnameA, 'rb'), clustsA)
    featvalsB = get_feat_vals_from_repo(gzip.open(fnameB, 'rb'), clustsB)
    featvalsC = get_feat_vals_from_repo(gzip.open(fnameC, 'rb'), clustsC)
    return '%d %s %s %s' % (labelnum,
                            ' '.join(['%d:%f' % (i,v) for i,v in enumerate(featvalsA)]),
                            ' '.join(['%d:%f' % ((i + len(featvalsA)), v) for i,v in enumerate(featvalsB)]),
                            ' '.join(['%d:%f' % ((i + len(featvalsA) + len(featvalsB)), v) for i,v in enumerate(featvalsC)]))

def get_feat_vals_from_repo(repofile, clusters):
    counts = [0 for f in clusters]
    numtoks = 0
    for toklines in get_individual_repo_files(repofile):
        words = [tok.strip() for tok in toklines]
        #used = set()
        for word in words:
            for i,clust in enumerate(clusters):
                if word in clust:
                    counts[i] += 1
                # NOTE we are not calculating number of files, but intstead
                # number of occurrences of the token.
                #if word in clust and word not in used:
                    #used.add(word)
                    #counts[i] += 1
        numtoks += len(words)
    return [float(x) / numtoks for x in counts]
    #return [float(x) / len(repo_filenames) for x in counts]

def get_individual_repo_files(repofile):
    cur = []
    for line in repofile:
        if is_delimiter_line(line):
            if len(cur) > 0:
                yield cur
            cur = []
        else:
            cur.append(line)
    yield cur

def is_delimiter_line(line):
    return '=!=!=' in line

def construct_lab_to_num_map(labs):
    return dict([(lab, i) for i,lab in enumerate(labs)])

def read_clusters(filename):
    clusts = []
    cur = set()
    for line in open(filename, 'r'):
        if re.match(r'\d+=====', line):
            if len(cur) > 0:
                clusts.append(cur)
                cur = set()
        else:
            cur.add(line.strip())
    clusts.append(cur)
    return clusts

def get_repo_to_pageranks_map(pagerank_vec_dirname, pagerank_cor_dirname):
    '''  takes directory name of pagerank vectors and pagerank dim-classname
    correspondences.  returns a dict sith
    {reponame -> {className -> pagerank}} mappings. Assumes that the files in
    the two directories are named after repositories.
    '''
    prs = dict()
    for vec_fname in os.listdir(pagerank_vec_dirname):
        pr_vec = [float(line.strip())
                  for line in open(os.path.join(pagerank_vec_dirname, vec_fname), 'r').readlines()]
        d = dict()
        for line in open(os.path.join(pagerank_cor_dirname, vec_fname), 'r'):
            toks = line.split()
            d[toks[0]] = pr_vec[int(toks[1])]
        prs[vec_fname] = d
    return prs

def get_repo_to_lab_map(labelfilename):
    return dict((url_to_reponame(line.split()[0]), line.split()[1])
                for line in open(labelfilename, 'r'))

def url_to_reponame(url):
    return url.split('/')[-1]

#def get_repo_to_filenames_map(repolistdirname):
#    return dict([(fname, [x.strip()
#                          for x in open(os.path.join(repolistdirname, fname), 'r').readlines()])
#                 for fname in os.listdir(repolistdirname)])

if __name__ == '__main__':
    if len(sys.argv) < 8:
        sys.stderr.write('not enough arguments\n')
        sys.exit()
    main(*sys.argv[1:])
