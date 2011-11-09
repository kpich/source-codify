#!/usr/bin/env python
''' Call with four params:
    - the directory containing a bunch of files, each of which is named with
      a repo's name, and the contents of which is a newline-delimited list of
      tokenized java files in that repo.
    - a file giving the labels of repos (newline delimited, each line
      containing a "repo-name   label" pair)
    - a filename with a newline-delimited list of
      features (each of which is just a token to look for)
    - the base name of the directory containing tokenized repo files
'''

import itertools
import os
import sys

def main(repolistdirname, labelfilename, featurefilename, repobasedirname):
    features = read_features(featurefilename)
    repo_to_lab_map = get_repo_to_lab_map(labelfilename)
    lab_to_num_map = construct_lab_to_num_map(set(repo_to_lab_map.values()))
    repo_to_filenames_map = get_repo_to_filenames_map(repolistdirname)
    for k,v in repo_to_lab_map.items():
        sys.stderr.write('extracting features from %s...\n' % k)
        print construct_libsvm_line(lab_to_num_map[v], repo_to_filenames_map[k],
                                    features, repobasedirname)

def construct_libsvm_line(labelnum, repo_filenames,
                          features, repobasedirname):
    ''' constructs features in same order as param 'features'.
    '''
    feat_vals = get_feat_vals_from_repo([os.path.join(repobasedirname, x)
                                         for x in repo_filenames],
                                        features)
    return '%d %s' % (labelnum, ' '.join(['%d:%f' % (i,v)
                                          for i,v in enumerate(feat_vals)]))

def get_feat_vals_from_repo(repo_filenames, features):
    feature_set = set(features)
    counts = [0 for f in features]
    numtoks = 0;
    for fname in repo_filenames:
        words = list(itertools.chain(*[line.split()
                                       for line in open(fname,'r').readlines()]))
        for word in words:
            if word in feature_set:
                counts[features.index(word)] += 1
        numtoks += len(words)
    return [float(x) / numtoks for x in counts]

def construct_lab_to_num_map(labs):
    return dict([(lab, i) for i,lab in enumerate(labs)])

def read_features(filename):
    return list(itertools.chain(*[li.split() for li in open(filename, 'r')]))

def get_repo_to_lab_map(labelfilename):
    return dict((url_to_reponame(line.split()[0]), line.split()[1])
                for line in open(labelfilename, 'r'))

def url_to_reponame(url):
    return url.split('/')[-1]

def get_repo_to_filenames_map(repolistdirname):
    return dict([(fname, [x.strip()
                          for x in open(os.path.join(repolistdirname, fname), 'r').readlines()])
                 for fname in os.listdir(repolistdirname)])

if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.stderr.write('Incorrect number of arguments\n')
        sys.exit()
    main(*sys.argv[1:])
