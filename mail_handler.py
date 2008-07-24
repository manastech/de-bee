from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from model import *
from mail_sender import *

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
