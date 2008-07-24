import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template
from hashlib import *
from serverUtils import UrlBuilder

class GroupInvitationHandler(webapp.RequestHandler):
		
	def get(self):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
			return		
		group = Group.get(self.request.get("group"))
		userEmail = self.request.get("user")
		invitation = GroupInvitation(group, userEmail, UrlBuilder(self.request))
		if invitation.makeHash() != self.request.get("hash"):
			self.response.out.write("Invitation is invalid") # TODO HTTP ERROR
			return		
		if user.email() != userEmail:
			self.response.out.write("This invitation is not for you.") # TODO HTTP ERROR
			return
		
		exists = Membership.gql("WHERE user = :1 AND group = :2", user, group).count() > 0
		if exists:
			self.response.out.write("You are already a member of %s group" % group.name)
		else:
			Membership(user=user,group=group,balance=0.0).put()
			self.response.out.write("You have been added to <a href='/group?group=%s'>%s</a> group" % (group.key(), group.name))
	
class GroupInvitation:
	
	def __init__(self, group, userEmail, urlBuilder):
		self.group = group
		self.userEmail = userEmail
		self.urlBuilder = urlBuilder
	
	def getUrl(self):
		return self.urlBuilder.buildUrl("/groupInvitation?group=%s&user=%s&hash=%s" % (str(self.group.key()) , self.userEmail , self.makeHash()))
	
	def makeHash(self):
		m = sha224()
		m.update(str(self.group.key()))
		m.update(self.userEmail)
		return m.hexdigest()
	