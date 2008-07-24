from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from model import *
import cgi
import os
import registration as registration

class MainHandler(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()
    reg = registration.Registration()
    if user:
		path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
		model = { 
			'username' : user.nickname(),
			'signout_url' : users.create_logout_url("/"),
			'debts' : self.getDebts(user),
			'groups' : self.getGroups(user),
			'isregistered' : reg.IsRegistered(user)
			}
		self.response.out.write(template.render(path, model))
    else:
		model = {'loginurl': users.create_login_url("/")}
  		path = os.path.join(os.path.dirname(__file__), 'introduction.html')
		self.response.out.write(template.render(path, model))
	
  def getDebts(self, user):	
	total = 0
	items = []
	for m in self.getRelevantMemberships(user):
		total += m.balance
		items.append({'isOweToSelf' : m.balance > 0, 'amount' : abs(m.balance), 'group' : m.group })
	return { 'isOweToSelf' : total > 0, 'total' : abs(total), 'items' : items }

  def getGroups(self, user):
	memberships = Membership.gql("WHERE user = :1", user)
	groups = map((lambda x: x.group), memberships)
	return groups

  def getRelevantMemberships(self, user):
	return Membership.gql("WHERE user = :1 AND balance != 0", user)
