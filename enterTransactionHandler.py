import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

class EnterTransactionHandler(webapp.RequestHandler):
	
	def get(self):
		currentGroup = Group.get("agZkZS1iZWVyCwsSBUdyb3VwGAEM")
		members = db.Query(Membership)
		members.filter('group =', currentGroup)
		#for member in members:
		#    print member.user
		
		path = os.path.join(os.path.dirname(__file__), 'enterTransaction.html')
		self.response.out.write(template.render(path, {'members': members}))