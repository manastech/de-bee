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
        if reg.IsRegistered(user):
			path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
			model = { 
				'username' : user.nickname(),
				'signout_url' : users.create_logout_url("/"),
				'debts' : self.getDebts(user),
				}
			self.response.out.write(template.render(path, model))
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
	
  def getDebts(self, user):	
	total = 0
	items = []
	for m in self.getRelevantMemberships(user):
		total += m.balance
		items.append({'isOweToSelf' : m.balance > 0, 'amount' : abs(m.balance), 'group' : m.group })
	return { 'isOweToSelf' : total > 0, 'total' : abs(total), 'items' : items }
	
  def getRelevantMemberships(self, user):
	return Membership.gql("WHERE user = :1 AND balance != 0", user)

class TransactionHistory(webapp.RequestHandler):
  def get(self):
  	
    if not users.get_current_user():      
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
    template_values = {}
    
    path = os.path.join(os.path.dirname(__file__), 'transactionHistory.html')
    self.response.out.write(template.render(path, template_values))

