#!/usr/bin/env python
''' Pass this two params:
    - The filename of "reponame label" pairs
    - The path containing the actual files.
'''
import tfidf
import glob,os
import sys

NUM_FEATS_PER_LABEL = 100;

FEATURES_DIR = 'features/'
IDF_FNAME = 'idf_file.txt'
STOPWORD_FNAME = 'stopwords.txt'

my_tfidf = tfidf.TfIdf();

token_labels = {}
labels = {}

def readLabels(file):
    print 'Reading labels from file ' + file
    fh = open(file,'r')
    for line in fh:
        w = line.split('\t')
        if(len(w) <2): continue
        #print line,len(w);
        labels[str(w[0])] = str(w[1].strip().replace('/', '_'))

def getLabel(file):
    n = 5
    w = file.split('/')
    return labels[w[n]]

def updateTokenforLabels(label, str2):
    if label not in token_labels:
        token_labels[label]={}
    
    for w in str2.split():
        if w not in token_labels[label]:
	    token_labels[label][w] = 1
        else:
	    token_labels[label][w] = token_labels[label][w] + 1

def scandirs(path):
    for currentFile in glob.glob( os.path.join(path, '*') ):
        if os.path.isdir(currentFile):
            #print 'got a directory: ' + currentFile
            scandirs(currentFile)
        else:
            #print 'Processing file' + currentFile
            label = getLabel(currentFile);
            tstr = open(currentFile, 'r').read()
            
            updateTokenforLabels(label,tstr)

            my_tfidf.add_input_document(tstr)


def getTfIdf(n,path):
    for label in token_labels:
        print "TFIDF for "+ label
        #print my_tfidf.get_doc_topkeywords(token_labels[label],n)
        writeTfIdf(path,label,my_tfidf.get_doc_topkeywords(token_labels[label],n))

def writeTfIdf(path,label,tfidf_k):
    fh = open(path+label+'.features','w')
    for w in tfidf_k:
        fh.write(str(w[0])+' '+str(w[1]) +'\n')
    fh.close()
        
def ensure_dir(filename):
    d = os.path.dirname(filename)
    if not os.path.exists(d):
        os.makedirs(d)

def main(label_fname, path_dirname):
    global my_tfidf
    readLabels(label_fname)
    scandirs(path_dirname)
    my_tfidf.save_corpus_to_file(IDF_FNAME, STOPWORD_FNAME)
    my_tfidf = tfidf.TfIdf(IDF_FNAME, STOPWORD_FNAME); 
    ensure_dir(FEATURES_DIR)
    getTfIdf(NUM_FEATS_PER_LABEL, FEATURES_DIR)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

