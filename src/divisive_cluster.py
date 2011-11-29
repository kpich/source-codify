#!/usr/bin/env python
''' Implements the divisive information-theoretic clustering algorithm as
    given in Dhillon et al.
'''

import gzip
import itertools
import math
import os
import sys

K = 1000
EPS = 0.001

def main(labels_fname, tok_corp_dirname):
    corp_labs = dict([(line.split()[0], line.split()[1])
                      for line in open(labels_fname, 'r')])
    #toks = get_all_toks(tok_corp_dirname)
    priors = calc_priors(tok_corp_dirname)
    conds = calc_conditionals(tok_corp_dirname, corp_labs)
    clusts = get_init_clusters(conds)
    refine_clusts(clusts, priors, conds)
    print_clusts(clusts)

def print_clusts(clusts):
    for i,c in enumerate(clusts):
        print '%d==================================' % i
        for tok in c:
            print tok

def refine_clusts(clusts, priors, conds):
    converged = False
    labs = get_list_of_labels(conds)
    old_clust_quality = None
    i = 0
    while True:
        sys.stderr.write('iteration %d:\n\n' % i)
        i += 1
        sys.stderr.write('%s\n' % str([len(c) for c in clusts]))

        #these two lines calculate step 2 in fig 1 of dhillon et al:
        clust_priors = get_clust_priors(clusts, priors)
        clust_conds = get_clust_conds(clusts, priors, clust_priors, conds, labs)
        clust_quality = get_clust_quality(clusts, priors, conds, clust_conds)
        sys.stderr.write('quality: %.9f\n' % clust_quality)
        if (old_clust_quality is not None) and \
           (math.fabs(clust_quality - old_clust_quality) < EPS):
            break;
        old_clust_quality = clust_quality

        # indices looks "topolotically" just like clusts but has the new indices instead.
        indices = [[get_new_clust_ind(w, conds[w], clust_conds) for w in clust]
                   for clust in clusts]
        clusts = create_new_clusts(clusts, indices)

def create_new_clusts(clusts, indices):
    '''reassigns words from 'clusts' to indices.
    '''
    newclusts = [[] for c in clusts]
    for i,clustinds in enumerate(indices):
        for j,newind in enumerate(clustinds):
            newclusts[newind].append(clusts[i][j])
    return newclusts

def get_new_clust_ind(w, cond, clust_conds):
    '''This is step 3 of Figure 1 in Dhillon et al.
    '''
    mindiv = sys.float_info.max
    minind = -1
    for i,clust_cond in enumerate(clust_conds):
        kl = kl_div(cond, clust_cond)
        if kl < mindiv:
            mindiv = kl
            minind = i
    assert minind != -1
    return minind

def get_clust_quality(clusts, priors, conds, clust_conds):
    return sum([sum([priors[w] * kl_div(conds[w], clust_conds[i])
                     for w in clust])
                for i,clust in enumerate(clusts)])

def kl_div(p1, p2):
    ''' returns KL divergence between two probability distributions.
        p1 and p2 must be dicts mapping {val -> prob}.
    '''
    return sum([prob1 * math.log((prob1 / p2[k]), 2)
                for k,prob1 in p1.items()])

def get_list_of_labels(conds):
    return set(itertools.chain(*[d.keys() for d in conds.values()]))

def get_clust_priors(clusts, priors):
    return [sum([priors[tok] for tok in clust])
            for clust in clusts]

def get_clust_conds(clusts, priors, clust_prior, conds, labs):
    '''returns an array of dicts mapping {label -> prob}.
       Note that the length of this array will be len(clusts).
    '''
    return [get_clust_cond_dict(clust, priors, clust_prior[i], conds, labs)
            for i,clust in enumerate(clusts)]

def get_clust_cond_dict(clust, priors, clust_prior, conds, labs):
    clust_dict = dict()
    for lab in labs:
        clust_dict[lab] = sum([conds[w][lab] * priors[w] / clust_prior
                               for w in clust])
    # in the case that the cluster is empty, we return a uniform pdf:
    if len(clust) == 0:
        clust_dict = dict([(lab, 1.0 / len(labs)) for lab in labs])
    return clust_dict

def get_init_clusters(conds):
    clust_dict = dict()
    for w, condmap in conds.items():
        bestlab = get_best_lab(w, condmap)
        li = clust_dict.setdefault(bestlab, [])
        li.append(w)
    clusts = []
    min_num_splits = K / len(clust_dict.values())
    #print 'min num %d' % min_num_splits
    for orig_clust in clust_dict.values():
        N = int(math.ceil(float(len(orig_clust)) / min_num_splits))
        if N == 0: N = 1
        #print 'splitting len %d into sublists of len %d' % (len(orig_clust), N)
        #print 'got %d sublists' % len(partition(orig_clust, N))
        clusts += partition(orig_clust, N)
    while len(clusts) < K:
        #print len(clusts)
        i = get_ind_of_longest_list(clusts)
        tosplit = clusts[i]
        clusts = clusts[:i] + clusts[i+1:]
        clusts += partition(tosplit, len(tosplit) / 2)
    #print len(clusts)
    return clusts

def get_ind_of_longest_list(clusts):
    ind = 0
    size = 0
    for i,c in enumerate(clusts):
        if len(c) > size:
            ind = i
            size = len(c)
    return ind

def partition(li, sublist_len):
    '''surely this is already written somewhere?'''
    num_sublists = int(math.ceil(float(len(li)) / sublist_len))
    return [li[i*sublist_len:(i+1)*sublist_len] for i in range(num_sublists)]

def get_best_lab(word, condmap):
    max_lab = ''
    curmax = 0;
    for k,v in condmap.items():
        if len(max_lab) == 0 or v > curmax:
            max_lab = k
            curmax = v
    assert len(max_lab) > 0
    return max_lab

def calc_priors(tok_corp_dirname):
    '''calculates the MLE estimate of the token priors.
       returns a map from token to probabilities.
    '''
    counts = dict()
    tot = 0
    for repo in get_repos(tok_corp_dirname):
        for tok in repo[1]:
            c = counts.get(tok, 0)
            counts[tok] = c + 1
            tot += 1
    return dict([(k, float(v) / tot) for k,v in counts.items()])

def calc_conditionals(tok_corp_dirname, labs):
    '''calculates smoothed MLE estimate of p(C|w).
       returns a map from words to {label -> prob} maps.
       so it returns something like {word -> {label -> prob}}.
       Currently uses simple Laplace smoothing.
    '''
    totcounts = dict()
    labcounts = dict()
    for repo in get_repos(tok_corp_dirname):
        lab = labs[repo[0]]
        for tok in repo[1]:
            tot_c = totcounts.get(tok, 0)
            totcounts[tok] = tot_c + 1
            thislab_counts = labcounts.setdefault(lab, dict())
            thislab_c = thislab_counts.get(tok, 0)
            thislab_counts[tok] = thislab_c + 1
    cond_dict = dict()
    for tok, tot_c in totcounts.items():
        word_dict = dict()
        numlabs = len(labcounts.keys())
        for lab in labcounts.keys():
            # commented out line does not perform smoothing.
            #word_dict[lab] = float(labcounts[lab].get(tok, 0)) / tot_c
            word_dict[lab] = float(labcounts[lab].get(tok, 0) + 1) / (tot_c + numlabs)
        cond_dict[tok] = word_dict
    return cond_dict

#def get_all_toks(dirname):
#    return set(itertools.chain(*[repo[1] for repo in get_repos(dirname)]))

def get_repos(dirname):
    '''generator of (corpname, [list of token]) pairs.
    '''
    for fname in os.listdir(dirname):
        yield (fname_to_reponame(fname), [x.strip()
                       for x in gzip.open(os.path.join(dirname, fname), 'r')
                       if not is_file_header_line(x)])

def fname_to_reponame(fname):
    return fname.replace('.gz', '')

def is_file_header_line(line):
    return '=!=!=' in line

def dbg_print_priors_and_conds(clust_priors, clust_conds):
        print 'PRIORS:'
        for prior in clust_priors:
            print prior
        print ''
        print ''
        print 'CONDS:'
        for cond in clust_conds:
            for k,v in cond.items():
                print k
                print v
                print ''

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
