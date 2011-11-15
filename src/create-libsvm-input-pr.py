#!/usr/bin/env python
''' This creates the libsvm input file but takes pageranks into account.

    Call with SIX (!!!) params:
    - the directory containing a bunch of files, each of which is named with
      a repo's name, and the contents of which is a newline-delimited list of
      tokenized java files in that repo.
    - a file giving the labels of repos (newline delimited, each line
      containing a "repo-name   label" pair)
    - a filename with a newline-delimited list of
      features (each of which is just a token to look for)
    - the base name of the directory containing tokenized repo files
    - the base name of the directory containing the pagerank vectors (just the
      values
    - the base name of the directory containing the pagerank dimension<->classname
      correspondences
'''

import itertools
import os
import sys

DEFAULT_PAGERANK = 0.001

def main(repolistdirname, labelfilename, featurefilename,
         repobasedirname, pagerankvecdirname, pagerankcordirname):
    features = read_features(featurefilename)
    repo_to_lab_map = get_repo_to_lab_map(labelfilename)
    lab_to_num_map = construct_lab_to_num_map(set(repo_to_lab_map.values()))
    repo_to_filenames_map = get_repo_to_filenames_map(repolistdirname)
    repo_to_pageranks_map = get_repo_to_pageranks_map(pagerankvecdirname, pagerankcordirname)
    for k,v in repo_to_lab_map.items():
        sys.stderr.write('extracting features from %s...\n' % k)
        try:
            lab_to_num_map[v]
            repo_to_filenames_map[k]
            print construct_libsvm_line(lab_to_num_map[v], repo_to_filenames_map[k],
                                        features, repobasedirname, repo_to_pageranks_map, k)
        except KeyError:
            sys.stderr.write('KeyError with repo: %s\n' % k)
    for lab,num in lab_to_num_map.items():
        sys.stderr.write('num: %d\tlabel: %s\n' % (num, lab))

def construct_libsvm_line(labelnum, repo_filenames, features,
                          repobasedirname, pageranks, reponame):
    ''' constructs features in same order as param 'features'.
    '''
    feat_vals = get_feat_vals_from_repo([os.path.join(repobasedirname, x)
                                         for x in repo_filenames],
                                        features, pageranks, reponame)
    return '%d %s' % (labelnum, ' '.join(['%d:%f' % (i,v)
                                          for i,v in enumerate(feat_vals)]))

def get_feat_vals_from_repo(repo_fnames, features, pageranks, reponame):
    feature_set = set(features)
    counts = [0 for f in features]
    prtots = [0 for f in features]
    numtoks = 0
    for fname in repo_fnames:
        words = list(itertools.chain(*[line.split()
                                       for line in open(fname,'r').readlines()]))
        used = set()
        for word in words:
            if word in feature_set and word not in used:
                used.add(word)
                counts[features.index(word)] += 1
                #conditional needed for inverse rank
                #if len(repo_fnames) == 1:
                #    prtots[features.index(word)] += 1.0
                #else:
                #    prtots[features.index(word)] += (1.0 - get_pagerank(pageranks, fname, reponame, len(repo_fnames)))
                prtots[features.index(word)] += get_pagerank(pageranks, fname, reponame, len(repo_fnames))
        numtoks += len(words)
    return prtots
    #if len(repo_fnames) <= 1:
    #    denom = 1
    #else:
    #    denom = len(repo_fnames) - 1
    #return [(1.0 / denom) * pr for pr in prtots]

    #if numtoks == 0: numtoks = 1
    #return [float(x) / numtoks + prtots[i] for i,x in enumerate(counts)]

def construct_lab_to_num_map(labs):
    return dict([(lab, i) for i,lab in enumerate(labs)])

def read_features(filename):
    return list(itertools.chain(*[li.split() for li in open(filename, 'r')]))

def get_pagerank(pageranks, fname, reponame, num_files):
    try:
        pr_dict = pageranks[reponame]
    except KeyError:
        # if we don't have pageranks for this repo then assign equal pagerank
        # to all files
        sys.stderr.write('repo %s\'s pagerank not found\n' % reponame)
        return 1.0 / num_files
    try:
        return pr_dict[get_classname_from_fname(fname)]
    except:
        sys.stderr.write('In repo %s, pagerank for class %s not found\n' % (reponame, get_classname_from_fname(fname)))
        return DEFAULT_PAGERANK

def get_classname_from_fname(fname):
    return os.path.basename(fname).replace('.java', '').replace('.tok', '')

def get_repo_to_pageranks_map(pagerank_vec_dirname, pagerank_cor_dirname):
    '''  takes directory name of pagerank vectors and pagerank dim-classname
    correspondences.  returns a dict sith
    {reponame -> {className -> pagerank}} mappings. Assumes that the files in
    the two directories are named after repositories.
    '''
    prs = dict()
    for vec_fname in os.listdir(pagerank_vec_dirname):
        try:
            pr_vec = [float(line.strip())
                      for line in open(os.path.join(pagerank_vec_dirname, vec_fname), 'r').readlines()]
            # we are getting a few vectors of +/- Inf. as a hack, just ignore them:
            if len(pr_vec) > 0 and (pr_vec[0] == float('Inf') or pr_vec[0] == float('-Inf')):
                sys.stderr.write('Inf eigenvector found for %s. Ignoring.\n' % vec_fname)
                continue
        except ValueError:
            sys.stderr.write('Nonreal (or otherwise malformed) eigenvector found for %s. Ignoring.\n' % vec_fname)
            continue
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

def get_repo_to_filenames_map(repolistdirname):
    return dict([(fname, [x.strip()
                          for x in open(os.path.join(repolistdirname, fname), 'r').readlines()])
                 for fname in os.listdir(repolistdirname)])

if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.stderr.write('Incorrect number of arguments\n')
        sys.exit()
    main(*sys.argv[1:])
