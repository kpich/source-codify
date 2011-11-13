import tfidf
import math
import glob,os

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
        labels[str(w[0])] = str(w[1].rstrip('\n'))

def getLabel(file):
    n = 5
    w = file.split('/')
    #print w
    return labels[w[n]]

def updateTokenforLabels(label, str2):
    if label not in token_labels:
        token_labels[label]={}
    else: 
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
            label = getLabel(currentFile);
            #print 'Processing file' + currentFile
            tstr = file2str(currentFile)
            
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
        

def file2str(file):
    fh = open(file,'r')
    str = "";
    for line in fh:
        str = str + line
    return str


def main():
    labelfile = './labeled-corpus-striped.txt'
    path = '/scratch/cluster/pichotta/dm-corpus-tokenized/'
    #path = '/Users/vinodh/fall2011/DM/repos/'
    num_features = 1000;

    readLabels(labelfile)
    scandirs(path)
    
    my_tfidf.save_corpus_to_file("idf_file.txt","stopword.txt")
    
    getTfIdf(num_features,'features/')

main()
