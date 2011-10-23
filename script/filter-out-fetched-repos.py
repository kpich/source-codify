
import json
import sys

def main(jsonfilename, urllistfilename):
    li = json.load(open(jsonfilename, 'r'))
    urls = set([proc_url(l.strip()) for l in open(urllistfilename, 'r')])
    print json.dumps(filter(lambda x: proc_url(x['url']) in urls,  li), indent=1)

def proc_url(url):
    res = url[url.find('//') + 2:]
    if url[-4:] == '.git':
        res = res[:-4]
    return res

    
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
