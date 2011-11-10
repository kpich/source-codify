#!/usr/bin/env python
''' Pass this
    - The base directory where the repos are to be found;
    - a bunch of filenames of files, one per repository. Each file
      must contain newline-delimited paths to all of the *.java files
      in the repository (these are paths to actualy *.java files, and
      not to tokenized files).

    This script prints a bunch of adjacency matrices, one for each project,
    in the CWD. It also prints a file giving the mapping between indices in
    the adjacency matrix (0-indexed) and the filenames
'''

import os
import re
import sys

def main(base_dirname, *proj_list_filenames):
    for fname in proj_list_filenames:
        java_files = [x.strip() for x in open(fname, 'r').readlines()]
        class_names = [get_classname_from_file(f) for f in java_files]
        class_name_map = dict([(c,i) for i,c in enumerate(class_names)])
        graph = [get_dep_list(os.path.join(base_dirname, f), class_name_map, len(java_files))
                 for f in java_files]
        print_graph_to_file(graph, 'depgraph-%s.txt' % os.path.basename(fname))
        print_file_index_mappings('index-filename-correspondences-%s.txt' %
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
    filetext = open(fname, 'r').read()
    for match in re.compile(r'new\s+(\w+)').finditer(filetext):
        if(match.group(1) in class_name_map):
            li[class_name_map[match.group(1)]] = 1
    return li

def get_classname_from_file(filename):
    fname = os.path.basename(filename)
    assert fname.endswith('.java')
    return fname[:-5]

if __name__ == '__main__':
    main(sys.argv[1], *sys.argv[2:])
