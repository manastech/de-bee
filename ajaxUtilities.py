from google.appengine.api import users

def out(request, str):
        request.response.out.write(str)
               
def script(str):
    return '<script>' + str + '</script>'

def feedback(div, msg):
    return show(div) + setInnerHtml(div, msg)

def show(div):
    return setStyleDisplay(div, '')

def hide(div):
    return setStyleDisplay(div, 'none')

def setStyleDisplay(div, value):
    return 'parent.document.getElementById("' + div + '").style.display = "' + value + '";'

def setInnerHtml(div, msg):
    return 'parent.document.getElementById("' + div + '").innerHTML = "' + msg + '";'

def alert(message):
    return 'alert("' + message + '");'

def redirect(location):
    str = 'host = "http://" + parent.location.host;'
    str = str + 'parent.location.href = host + "' + location + '";'
    return str

def alertMessage(request,message):
    out(request,script(alert(message)))
    
def redirectPage(request,location):
    out(request, script(redirect(location)))
    
def authenticatedUser(request):
    user = users.get_current_user()
    if user is None:
        error = 'You must be logged in to do this.'
        alertMessage(request,error)
        return False
    else:
        return True
    