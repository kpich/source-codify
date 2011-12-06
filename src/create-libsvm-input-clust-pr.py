#!/usr/bin/env python
''' This creates the libsvm input file but takes pageranks into account.

    Call with the following 5 params:
    - the directory containing a bunch of gzipped files, each of which contains
      the newline-delimited tokenized repo (with delimiters between files)
    - a file giving the labels of repos (newline delimited, each line
      containing a "repo-name   label" pair)
    - a filename containing the clusters (as output by the divisive clustering script)
    - the base name of the directory containing the pagerank vectors (just the
      values
    - the base name of the directory containing the pagerank dimension<->classname
      correspondences
'''

import gzip
import itertools
import os
import re
import sys

DEFAULT_PAGERANK = 0.001

# we multiply our pageranks by this to keep our sums from being too low
MULT_FACTOR = 100

def main(repofiledirname, labelfilename, clustfilename,
         pagerankvecdirname, pagerankcordirname):
    clusters = read_clusters(clustfilename)
    repo_to_lab_map = get_repo_to_lab_map(labelfilename)
    lab_to_num_map = construct_lab_to_num_map(set(repo_to_lab_map.values()))
    #repo_to_filenames_map = get_repo_to_filenames_map(repolistdirname)
    repo_to_pageranks_map = get_repo_to_pageranks_map(pagerankvecdirname, pagerankcordirname)
    for k,v in repo_to_lab_map.items():
        sys.stderr.write('extracting features from %s...\n' % k)
        try:
            lab_to_num_map[v]
            repo_fname = get_file_for_repo(k, repofiledirname)
            print construct_libsvm_line(lab_to_num_map[v], gzip.open(repo_fname, 'rb'),
                                        clusters, repo_to_pageranks_map, k)
        except (KeyError, AssertionError):
            sys.stderr.write('KeyError with repo: %s\n' % k)
    for lab,num in lab_to_num_map.items():
        sys.stderr.write('num: %d\tlabel: %s\n' % (num, lab))

def get_file_for_repo(reponame, repofiledirname):
    for fname in os.listdir(repofiledirname):
        if os.path.basename(fname).replace('.gz', '') == reponame:
            return os.path.join(repofiledirname, fname)
    assert False

def construct_libsvm_line(labelnum, repofile, clusters, pageranks, reponame):
    ''' constructs features in same order as param 'features'.
    '''
    feat_vals = get_feat_vals_from_repo(repofile, clusters, pageranks, reponame)
    return '%d %s' % (labelnum, ' '.join(['%d:%f' % (i,v)
                                          for i,v in enumerate(feat_vals)]))

def get_feat_vals_from_repo(repofile, clusters, pageranks, reponame):
    counts = [0 for c in clusters]
    #prtots = [0 for f in features]
    numtoks = 0
    repofiles = [x for x in get_individual_repo_files(repofile)]
    for fname,flines in repofiles:
        words = [x.strip() for x in flines]
        #used = set()
        for word in words:
            #if word in feature_set and word not in used:
            for i,clust in enumerate(clusters):
                if word in clust:
                    # regular PR:
                    # counts[i] += MULT_FACTOR * get_pagerank(pageranks, fname, reponame, len(repofiles))

                    # weighted-sum PR:
                    # counts[i] += MULT_FACTOR * get_pagerank(pageranks, fname, reponame, len(repofiles))

                    # reverse-ranked PR:
                    if len(repofiles) == 1:
                        counts[i] += float(MULT_FACTOR)
                    else:
                        counts[i] += MULT_FACTOR * (1.0 - get_pagerank(pageranks, fname, reponame, len(repofiles)))
        numtoks += len(words)

    #normal pr
    #if numtoks == 0: numtoks = 1
    #return [x / numtoks for x in counts]

    # reverse-ranked pr:
    if numtoks == 0:
        denom = 1
    else:
        denom = numtoks
    return [(1.0 / denom) * x for x in counts]

    #if numtoks == 0: numtoks = 1
    #return [float(x) / numtoks + prtots[i] for i,x in enumerate(counts)]

def get_individual_repo_files(repofile):
    ''' generator for duples (fname, file_lines) for all files in repo
    '''
    cur = []
    for line in repofile:
        if is_delimiter_line(line):
            if len(cur) > 0:
                yield curname, cur
            curname = get_name_from_delimiter(line)
            cur = []
        else:
            cur.append(line)
    yield curname, cur

def get_name_from_delimiter(line):
    return line.replace('=!=!=', '').strip()

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

#def get_repo_to_filenames_map(repolistdirname):
#    return dict([(fname, [x.strip()
#                          for x in open(os.path.join(repolistdirname, fname), 'r').readlines()])
#                 for fname in os.listdir(repolistdirname)])

if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.stderr.write('Incorrect number of arguments\n')
        sys.exit()
    main(*sys.argv[1:])
