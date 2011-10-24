import json
import shutil
import web
from web import form

DEFAULT_CLASSTYPE = '(select type)'
DATA_FILENAME = 'data/urls.dat'
BAK_FILENAME = 'data/urls.dat.bak'
class_names = [DEFAULT_CLASSTYPE,
               'development',
               'graphics',
               'databases',
               'networking',
               'mobile',
               'webapps',
               'loggers',
               'editors/IDE',
               'games',
               'other']

def get_classval(val):
    if val == None: return DEFAULT_CLASSTYPE
    return val

def get_forms():
    return [form.Dropdown(name='classlabel%d' % i,
                          args=class_names,
                          value = get_classval(pair[1]),
                          description = '<a href="%s">%s</a>' % (pair[0], pair[0]))
            for i,pair in enumerate(url_labels)]

def read_url_labels():
    f = open(DATA_FILENAME, 'r')
    li = []
    for line in f:
        toks = line.split()
        if len(toks) == 2:
            li.append((toks[0], toks[1]))
        else:
            li.append((toks[0], None))
    f.close()
    return li

def get_indiv_label_from_form(index):
    if class_form['classlabel%d' % index].value == DEFAULT_CLASSTYPE:
        return None
    return class_form['classlabel%d' % index].value

def get_url_labels_from_form():
    li = []
    for i in range(len(url_labels)):
        li.append((url_labels[i][0], get_indiv_label_from_form(i)))
    return li

def write_url_labels_to_file():
    global url_labels
    shutil.copy(DATA_FILENAME, BAK_FILENAME)
    url_labels = get_url_labels_from_form()
    f = open(DATA_FILENAME, 'w')
    for pair in url_labels:
        if pair[1] is None:
            f.write('%s\n' % pair[0])
        else:
            f.write('%s\t%s\n' % pair)
    f.close()

urls = (
  '/', 'annotator')
app = web.application(urls, globals(), autoreload=True)
render = web.template.render('templates/')
url_labels = read_url_labels()
class_form = form.Form(*get_forms())

class annotator:
    def GET(self):
        return render.mainmenu(class_form)

    def POST(self): 
        # whoa, validates has side effects! we need this call :c
        if not class_form.validates():
            return render.mainmenu(class_form)
        else:
            write_url_labels_to_file()
            return render.mainmenu(class_form)

if __name__ == "__main__":
    app.run()
