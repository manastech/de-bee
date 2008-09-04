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
		
		# verificar que la invitacion es valida (coinciden los hashes)
		isValidInvitation = invitation.makeHash() == self.request.get("hash")
		# verificar que el usuario logueado coincide con el mail de la invitacion
		isValidUser = user.email() == userEmail
		# verificar que el usuario no sea miembro del grupo
		isMember = Membership.gql("WHERE user = :1 AND group = :2", user, group).count() > 0
			
		template_values = {
			'isValidInvitation': isValidInvitation,
			'isValidUser': isValidUser,
			'isMember': isMember,
			'group': group,
			'currentUser': user,
			'signout_url': users.create_logout_url("/"),
			 }
			
		path = os.path.join(os.path.dirname(__file__), 'groupInvitation.html')
		self.response.out.write(template.render(path, template_values))
	
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
	
class GroupJoinHandler(webapp.RequestHandler):
	
	def post(self):
		user = users.get_current_user()
		group = Group.get(self.request.get("group"))
		alias = self.request.get("alias")
		
		if alias == "": # verificar que el alias no sea vacio
			self.response.out.write('<html><body><pre>')
			self.response.out.write("Alias name is required. <a href='javascript:history.back()'>Go back</a>.")
			self.response.out.write('</pre></body></html>')
			return
		elif self.isAliasTaken(alias): # verificar que el usuario no sea miembre de un grupo con el mismo alias seleccionado
			self.response.out.write('<html><body><pre>')
			self.response.out.write("You already have a Group with the selected alias, please select another name. <a href='javascript:history.back()'>Go back</a>.")
			self.response.out.write('</pre></body></html>')
			return
		else: # todo ok, hacerlo miembro
			Membership(user=user,group=group,balance=0.0,alias=alias).put()
			self.redirect("/group?group=%s" % group.key())
		
	def isAliasTaken(self,alias):
		user = users.get_current_user()
		return Membership.gql("WHERE user = :1 AND alias = :2", user, alias).count() > 0
