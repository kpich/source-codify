#!/usr/bin/env python
''' Pass this
- The base directory where the repos are to be found;
- a bunch of gzipped filenames where each file contains the tokens
for each .java file in a repo. The tokens should all be newline delimited
and each "java" file should be separtated by a line of the form
'=!=!= <path.java.tok> =!=!=' ).

This script prints a bunch of adjacency matrices, one for each project,
in the CWD. It also prints a file giving the mapping between indices in
the adjacency matrix (0-indexed) and the filenames
'''

import os
import re
import sys
import gzip

def main(base_dirname, *proj_list_filenames):

    for fname in proj_list_filenames:
        java_files = split_files(gzip.open(fname, 'rb').readlines())        
        class_names, class_names_lower = get_classname_from_file(java_files)
        class_name_map = dict([(c,i) for i,c in enumerate(class_names)])
        class_name_lower_map = dict([(c,i) for i,c in enumerate(class_names_lower)])
        graph = [get_dep_list(f, class_name_lower_map, len(class_names))
                 for f in java_files]
        print_graph_to_file(graph, 'dense-depgraph-%s.txt' % os.path.basename(fname))
        print_file_index_mappings('dense-index-filename-correspondences-%s.txt' %
                                  os.path.basename(fname), class_name_map)

def print_graph_to_file(graph, fname):
    f = open(fname, 'w')
    for row in graph:
        f.write('%s\n' % ','.join([str(x) for x in row]))
    f.close()

def print_file_index_mappings(fname, class_name_map):
    f = open(fname, 'w')
    for k,v in class_name_map.items():
        f.write('%s\t%d\n' % (k,v))
    f.close()
    

def get_dep_list(fname, class_name_map, numfiles):
    ''' returns a row of the dependency graph
'''
    li = [0 for i in range(numfiles)]

    for line in fname:
        if (line in class_name_map):
            li[class_name_map[line]] = 1
    return li

def split_files(whole_file):
    all_files = []
    current_file = []
    flag = 0
    for line in whole_file:
        line = line.strip()
        if line.startswith('=!=!='):
            if flag == 0:
                flag = 1
            else:
                all_files.append(current_file)
                current_file = []
        current_file.append(line)
    if not current_file:
        all_files.append(current_file)

    return all_files

def get_classname_from_file(all_files):
    classnames = []
    classnames_lower = []
    for cur_file in all_files:
        line = cur_file[0]
        assert line.startswith('=!=!=')
        assert line.endswith('.java.tok =!=!=')
        line = line[6:-15]
        classnames.append(os.path.basename(line))
        classnames_lower.append(os.path.basename(line).lower())
    return [classnames, classnames_lower]

if __name__ == '__main__':
    main(sys.argv[1], *sys.argv[2:])


