import cgi
from google.appengine.ext import webapp
from model import *
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

class EnterTransactionHandler(webapp.RequestHandler):
	
	def get(self):
		self.response.out.write("""
      <html>
        <body>
          <form action="/registerTransaction" method="post">
          	<div>From: <input type="text" value="Ary" name="fromUser"/></div>
          	<div>To: <input type="text" value="Nico" name="toUser"/></div>
          	<div>Amount: <input type="text" value="$15.000" name="amount"/></div>
          	<div>Reason: <input type="text" value="Trola francesa" name="reason"/></div>
            <div><input type="submit" value="Register"></div>
          </form>
        </body>
      </html>""")

		
class RegisterTransactionHandler(webapp.RequestHandler):
	
	def post(self):
		self.response.out.write('<html><body><pre>')
		self.response.out.write(cgi.escape(self.request.get('fromUser')))
		self.response.out.write(' owes ')
		self.response.out.write(cgi.escape(self.request.get('amount')))
		self.response.out.write(' to ')
		self.response.out.write(cgi.escape(self.request.get('toUser')))
		self.response.out.write(' because of ')
		self.response.out.write(cgi.escape(self.request.get('reason')))
		self.response.out.write('</pre></body></html>')