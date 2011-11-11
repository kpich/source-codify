#!/usr/bin/env python

import sys
import os
import re

def tokenize_comment(line):

    ind_block = line.find("*/")
    if (ind_block == -1):
        subwords = re.findall('[A-Z][A-Z]*[a-z]*|[a-z]+', line)
        return [subwords, True] #return tokenize list and true that still in comment
    else:
        splitline = line.split('*/', 1)
        subwords = re.findall('[A-Z][A-Z]*[a-z]*|[a-z]+', splitline[0])

        retVal = tokenize_nonComment(splitline[1])
        subwords.extend(retVal[0])
        return [subwords, retVal[1]]
        
def tokenize_nonComment(line):

    ind_inline = line.find("//")
    ind_block = line.find("/*")

    if ((ind_inline < ind_block or ind_block == -1) and ind_inline >= 0):
        m = re.search('(?<=//).+', line)
        
        if (m != None):
            subwords = re.findall('[A-Z][A-Z]*[a-z]*|[a-z]+', m.group(0))
            return [subwords, False]
        else:
            return [[], False]

    elif ((ind_inline > ind_block or ind_inline == -1) and ind_block >= 0):
        m = re.search('(?<=/\*).+', line)
        if (m == None):
            subwords = []
            return [ subwords, True]
        else:            
            return tokenize_comment(m.group(0)) 
    else:
        return [ [], False]

def main():
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    whole = int(sys.argv[3]) 

    tokens = []
    lines = []

    f_in = open(in_file, 'r');
    
    if (whole == 1):
        subwords = re.findall('[A-Z][A-Z]*[a-z]*|[a-z]+', f_in.read())            
        tokens.extend(map(lambda x : x.lower(), subwords))
 
    if (whole == 0):
        inComment = False
        for line in f_in:

            if (inComment == False):
                retVal = tokenize_nonComment(line)                
            else:
                retVal = tokenize_comment(line)
            inComment = retVal[1]
            tokens.extend(map(lambda x : x.lower(), retVal[0]))

    f_in.close()

    f_out = open(out_file, 'w');
    for token in tokens:
        f_out.write(token +'\n')

    f_out.close()            
                


        


if __name__ == '__main__':
    main()
