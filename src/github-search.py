#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import json
import pycurl

base_url = 'http://github.com/api/v2/json/repos/search/*?language=Java'

json_str = ''
def write_callback(buf):
    global json_str
    json_str += buf

def search():
    global json_str
    json_repo_li = []
    for i in range(1,21):
        json_str = ''
        curl = pycurl.Curl()
        curl.setopt(curl.WRITEFUNCTION, write_callback)
        url = '%s&start_page=%d' % (base_url, i)
        curl.setopt(curl.URL, url)
        curl.perform()
        li = json.loads(json_str)["repositories"]
        #print 'API call got %d new repos' % len(li)
        json_repo_li += li
        curl.close()
    print json.dumps(json_repo_li, indent=1)
    #print 'Total: %d repos' % len(json_repo_li)
    #for repo in json_repo_li:
      #print repo["name"]
      #if 'description' in repo:
          #print '\t%r' % repo["description"]
      #else:
          #print '[no description]'

if __name__  == '__main__':
    search()
