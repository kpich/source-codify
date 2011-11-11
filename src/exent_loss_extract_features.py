#!/usr/bin/env python
''' Figures out which features to use, using expected entropy loss.

    Call with three params (note these are three of the four params that
    create_libsvm_input needs):
    - the directory containing a bunch of files, each of which is named with
      a repo's name, and the contents of which is a newline-delimited list of
      tokenized java files in that repo.
    - a file giving the labels of repos (newline delimited, each line
      containing a "repo-name   label" pair)
    - the base name of the directory containing tokenized repo files

    We implement the MLE estimates of the probabilities as given in Ugurel
    et al 2002, but for the feature-related probabilities, our "examples"
    are files instead of repos (otherwise we have far too little data to
    get reliable numbers). Our class priors, however, are based on repos.
    (so another way of saying this is we have the tacit accumption that each
    class uniformly distributes its tokens amongst its files)

    Also holy jeez this is some of the worst python I've ever written!
'''

import itertools
import math
import operator
import os
import sys

# if a word appears in too few files, we don't consider it for featurehood:
MIN_NUM_FILE_APPEARANCES = 2

# the number of features to extract per class
NUM_FEATS_PER_CLASS = 100

EPS = 0.001

def main(repo_tokfilelist_dir, labels_fname, repo_basedir):
    repo_lab_map = get_repo_to_lab_map(labels_fname)
    repo_fname_map = get_repo_to_filenames_map(repo_tokfilelist_dir)
    class_to_repos_map = get_class_to_repos_map(repo_lab_map)
    per_class_feat_counts = get_per_class_feat_counts(repo_fname_map, repo_basedir, repo_lab_map, class_to_repos_map)
    all_feat_counts = get_all_candidate_feat_counts(per_class_feat_counts)
    num_files = get_num_files(repo_fname_map)
    class_prior_map = get_class_priors(repo_lab_map)
    feat_prior_map = get_feat_priors(all_feat_counts, num_files)
    c_given_f_map = get_c_given_f_map(per_class_feat_counts,
                                      all_feat_counts)
    c_given_f_bar_map = get_c_given_f_bar_map(per_class_feat_counts,
                                              all_feat_counts,
                                              get_class_to_fnames_map(class_to_repos_map, repo_fname_map),
                                              num_files)
    class_exent_loss_map = calc_class_exent_loss_map(class_prior_map,
                                                     feat_prior_map,
                                                     c_given_f_map,
                                                     c_given_f_bar_map)
    print_top_features(class_exent_loss_map)
#    print 'numfiles: %d' % num_files
#    print class_prior_map
#    print feat_prior_map
#    print c_given_f_map 
#    print c_given_f_bar_map 

def print_top_features(class_exent_loss_map):
    for cl, eel_dict in class_exent_loss_map.iteritems():
        print '----------------------'
        print 'top %d features for class %s:' % (NUM_FEATS_PER_CLASS, cl)
        print '----------------------'
        sorted_ents = sorted(eel_dict.iteritems(), key=operator.itemgetter(1), reverse=True)
        for feat,val in sorted_ents[:NUM_FEATS_PER_CLASS]:
            print '%s\t(%f)' % (feat, val)

def calc_class_exent_loss_map(class_prior_map, feat_prior_map, c_given_f_map, c_given_f_bar_map):
    ''' calculates expected entropy loss for a feature in a class. So we return
        a dict mapping classnames to dicts, each of which maps a feature to
        an expected entropy loss. That is, {Class -> {feature, EEL}}.
    '''
    class_prior_entropies = calc_class_prior_ents(class_prior_map)
    class_present_posterior_entropies = calc_class_present_posterior_ents(c_given_f_map)
    class_absent_posterior_entropies = calc_class_absent_posterior_ents(c_given_f_bar_map)
    return dict([(cl, dict([(f, calc_EEL(cl,
                                         f,
                                         class_prior_entropies,
                                         class_present_posterior_entropies,
                                         class_absent_posterior_entropies,
                                         feat_prior_map))
                            for f,dummy in fdict.iteritems()]))
                 for cl,fdict in class_present_posterior_entropies.items()])

def calc_class_prior_ents(class_prior_map):
    return dict([(cl, calc_ent(pr))
                for cl,pr in class_prior_map.items()])

def calc_class_present_posterior_ents(c_given_f_map):
    return dict([(cl, dict([(f, calc_ent(pr)) for f,pr in fdict.items()]))
                for cl,fdict in c_given_f_map.items()])
    
def calc_class_absent_posterior_ents(c_given_f_bar_map):
    return dict([(cl, dict([(f, calc_ent(pr)) for f,pr in fdict.items()]))
                for cl,fdict in c_given_f_bar_map.items()])
    
def calc_ent(prob):
    if prob == 0:
        prob = EPS
    if prob == 1:
        prob -= EPS
    return -(prob * math.log(prob, 2)) - ((1.0 - prob) * math.log(1.0 - prob, 2))

def calc_EEL(class_lab, feat_lab, prior_ents, pos_posterior_ents, neg_posterior_ents, feat_priors):
    return (prior_ents[class_lab] -
           (pos_posterior_ents[class_lab][feat_lab] * feat_priors[feat_lab]) +
           (neg_posterior_ents[class_lab][feat_lab] * (1.0 - feat_priors[feat_lab])))

def get_c_given_f_map(per_class_feat_counts, all_feat_counts):
    ''' calculates p(C|f) for class C, feature f. This actually returns a
        dict mapping from classname -> dicts, each of which maps tokens to
        probabilities. That is, {classname -> {feature -> probability}}.
    '''
    return dict([(c, dict([(f, float(count) / all_feat_counts[f])
                           for f,count in fcdict.iteritems()]))
                 for c,fcdict in per_class_feat_counts.iteritems()])

def get_c_given_f_bar_map(per_class_feat_counts, all_feat_counts, class_to_fnames_map, num_files):
    ''' Like get_c_given_f_map, but returns p(C|~f) rather than p(C|f).
    '''
    # i am going to do this iteratively because otherwise there is a 0% chance
    # anyone will be able to read it
    res = dict()
    for c, fcdict in per_class_feat_counts.iteritems():
        thisdict = dict()
        for f,count in fcdict.iteritems():
            posExamplesWithoutF = len(class_to_fnames_map[c]) - count
            examplesWithoutF = num_files - all_feat_counts[f]
            # print '%s, %s, %d' % (c, f, count)
            # print 'pos: %d\tall: %d' % (posExamplesWithoutF, examplesWithoutF)
            if examplesWithoutF == 0:
                # if there are no examples without f, then set the conditional
                # prob here equal to the prior 
                thisdict[f] = float(len(class_to_fnames_map[c])) / num_files
            else:
                thisdict[f] = float(posExamplesWithoutF) / examplesWithoutF
        res[c] = thisdict
    return res

def get_class_priors(repo_lab_map):
    labs = set(repo_lab_map.values())
    num_repos = len(repo_lab_map)
    return dict([(lab, float(repo_lab_map.values().count(lab)) / num_repos)
                for lab in labs])

def get_feat_priors(feat_counts, num_files):
    return dict([(k, float(v) / num_files) for k,v in feat_counts.items()])

def get_class_to_fnames_map(class_to_repos_map, repo_fname_map):
    return dict([(cl, list(itertools.chain(*[repo_fname_map[r] for r in repos])))
                 for cl,repos in class_to_repos_map.items()])

def get_num_files(repo_fname_map):
    return sum([len(v) for v in repo_fname_map.values()])

def get_all_candidate_feat_counts(per_class_feat_counts):
    return get_feats_to_total_counts_dict(per_class_feat_counts)

def get_per_class_feat_counts(repo_fname_map, repo_basedir, repo_lab_map, class_to_repos_map):
    ''' goes through files, returns a dict mapping class names to dicts,
        each of which maps words to the number of (in-class) files in which they
        appear. Throws away any tokens appearing in fewer than
        MIN_NUM_FILE_APPEARANCES files total .
    '''
    counts = dict()
    for lab,repos in class_to_repos_map.items():
        class_counts = dict()
        for repo in repos:
            for fname in repo_fname_map[repo]:
                already_added = set()
                for tok in get_tokens_from_file(os.path.join(repo_basedir, fname)):
                    if tok not in already_added:
                        c = class_counts.setdefault(tok, 0)
                        class_counts[tok] = c+1
                        already_added.add(tok)
        counts[lab] = class_counts
    trim_insufficiently_common_words(counts)
    return counts

def get_class_to_repos_map(repo_lab_map):
    labs = set(repo_lab_map.values())
    res = dict([(lab, [repo for repo,lab2 in repo_lab_map.items() if lab2 == lab])
               for lab in labs])
    return res

def trim_insufficiently_common_words(counts):
    delenda = get_delenda(counts)
    for c,di in counts.items():
        for tok,count in di.items():
            if tok in delenda:
                del di[tok]

def get_delenda(counts):
    total_counts = get_feats_to_total_counts_dict(counts)
    return set([k for k,v in total_counts.items()
                  if v < MIN_NUM_FILE_APPEARANCES])

def get_feats_to_total_counts_dict(counts):
    res = dict()
    for c,di in counts.items():
        for tok,count in di.items():
            c = res.setdefault(tok, 0)
            res[tok] = c + count
    return res

def get_tokens_from_file(fname):
    ''' generator returning tokens in file
    '''
    f = open(fname, 'r')
    for line in f:
        for tok in line.split():
            if len(tok) > 0:
                yield tok
    f.close()


# following three functions unceremoniously copy/pasted from create_libsvm_input
def get_repo_to_lab_map(labels_fname):
    return dict((url_to_reponame(line.split()[0]), line.split()[1])
                for line in open(labels_fname, 'r'))

def url_to_reponame(url):
    return url.split('/')[-1]

def get_repo_to_filenames_map(repolistdirname):
    return dict([(fname, [x.strip()
                          for x in open(os.path.join(repolistdirname, fname), 'r').readlines()])
                 for fname in os.listdir(repolistdirname)])

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write("wrong number of args\n")
        sys.exit()
    main(*sys.argv[1:])
