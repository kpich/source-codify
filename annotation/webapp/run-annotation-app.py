import web
from web import form

urls = (
  '/', 'hello')

app = web.application(urls, globals(), autoreload=True)
render = web.template.render('templates/')


DEFAULT_CLASSTYPE = '(select type)'
class_names = [DEFAULT_CLASSTYPE, 'type1', 'type2', 'type3']

dropdown_form = form.Form( 
    form.Dropdown(name='class',
                  args=class_names,
                  value = DEFAULT_CLASSTYPE
                 ))

class hello:
    def GET(self):
        my_form = dropdown_form()
        return render.hello(my_form)

    def POST(self): 
        my_form = dropdown_form() 
        if not my_form.validates(): 
            return render.hello(my_form)
        else:
            return 'you selected %s' % my_form['class'].value

if __name__ == "__main__":
    app.run()
