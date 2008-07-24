import cgi
from google.appengine.ext import webapp
from model import *
from mail_sender import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

class RegisterInviteHandler(webapp.RequestHandler):
	
	def post(self):
		group = Group.get(self.request.get('group'))
		invitationText = self.request.get('invitationText')
		emails = self.request.get('emails')
		emails = emails.split(',')
		
		sender = MailSender()
		for email in emails:
			email = email.strip()
			sender.sendInvitationMail(email, group.name, invitationText)
		self.response.out.write("Your invite has been sent!")