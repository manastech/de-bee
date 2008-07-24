from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from mail_sender import *
from model import *
import cgi
import os
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
			path = os.path.join(os.path.dirname(__file__), 'introduction.html')
			model = { 
				'username' : user.nickname(),
				'signout_url' : users.create_logout_url("/"),
				}
			self.response.out.write(template.render(path, model))
    else:
        greeting = ("<a href=\"%s\">Sign in or register</a>." %
                      users.create_login_url("/"))
	self.response.out.write("<html><body>%s</body></html>" % greeting)

class TransactionHistory(webapp.RequestHandler):
  def get(self):
  	
    if not users.get_current_user():      
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
    template_values = {}
    
    path = os.path.join(os.path.dirname(__file__), 'transactionHistory.html')
    self.response.out.write(template.render(path, template_values))

class MailHandler(webapp.RequestHandler):

	def get(self):
		mail_sender = MailSender()
		mail_sender.sendInvitationMail("jorge@manas.com.ar", "el nombre del grupo", "estas invitado che!")
		mail_sender.sendNoticeTransaction("jonat@manas.com.ar", "jorge@manas.com.ar", "un grupo", None)
		self.response.out.write("""
			<html>
			<body>
			Ya lo mande
			</body>
			</html>""")
