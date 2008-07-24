import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template
from hashlib import *

class GroupInvitationHandler(webapp.RequestHandler):
		
	def get(self):
		pass
	
class GroupInvitation:
	
	def __init__(self, group, invitedUser):
		self.group = group
		self.invitedUser = invitedUser
	
	def getUrl(self):
		return '/groupInvitation?group=' + str(self.group.key()) + '&user=' + str(self.invitedUser.email()) + '&hash=' + self.makeHash()

	def makeHash(self):
		m = sha224()
		m.update(str(self.group.key()))
		m.update(self.invitedUser.email())
		return m.hexdigest()
	