from google.appengine.ext import webapp
from google.appengine.api import users
import registration as registration

class MainHandler(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    reg = registration.Registration()
    if user:
        if reg.IsRegistered(user):
            greeting = ("Welcome, %s!  (<a href=\"%s\">sign out</a>)" %
                      (user.nickname(), users.create_logout_url("/")))
        else:
            greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)  <br><br>TODO: Introduction De-Bee" %
                      (user.nickname(), users.create_logout_url("/")))
    
    else:
        greeting = ("<a href=\"%s\">Sign in or register</a>." %
                      users.create_login_url("/"))

    self.response.out.write("<html><body>%s</body></html>" % greeting)

