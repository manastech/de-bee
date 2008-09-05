import cgi
from google.appengine.ext import webapp
from model import *
from mail_sender import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template
from serverUtils import UrlBuilder

class RegisterInviteHandler(webapp.RequestHandler):
	
	def post(self):
		group = Group.get(self.request.get('group'))
		invitationText = self.request.get('invitationText')
		emails = self.request.get('emails')
		emails = emails.split(',')
		user = users.get_current_user()
		
		sender = MailSender()
		for email in emails:
			email = email.strip()
			sender.sendInvitationMail(user, email, group, invitationText, UrlBuilder(self.request))
		self.redirect("/group?group=" + self.request.get('group') + "&msg=" + cgi.escape("Your invite has been sent!"))