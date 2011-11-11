#!/bin/bash

#first arg is for type of parsing-    0 for comments only        1 for all
#after first you can have arbitrary number of files listed
#each file listed as an arg should itself be a list of paths to other files
#this list of paths should be one per line and newline after each full path name
#you can have either .java or README files (or mix of both) listed
#for each .java/README a new file with the tokenized data will be placed in the same directory as original file
#the .tok extention will be appended to the name. (.../*.java.tok   or ../README.tok

idx=1
testIdx=1
str1='README'
tokExten=".tok"
DIR="$( cd "$( dirname "$0" )" && pwd )"

for arg in "$@"
do
    if [ $idx -eq $testIdx ] ; then
        parseOp=${arg}
        idx=2
    else

        while read line
        do
        fName=`basename "$line"`
        dName=`dirname "$line"`
        if [ $fName == $str1 ]; then
            out_filename=$line$tokExten
            python $DIR/tokenizer.py $line $out_filename 1
        else      
            out_filename="$dName/$fName$tokExten"
            echo $parseOp
            echo $line
            echo $out_filename
            python $DIR/tokenizer.py "$line" "$out_filename" $parseOp
        fi
        done < ${arg}
    fi
    
done
