import json
import sys

def main(jsonfilename):
    li = json.load(open(jsonfilename, 'r'))
#    names = [x['name'] for x in li]
#    for n in sorted(names):
#        print n.encode('utf-8')
    for repo in li:
        if 'name' in repo:
            print repr(repo["url"])

if __name__ == '__main__':
    main(sys.argv[1])
