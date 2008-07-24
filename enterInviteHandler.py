import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

class EnterInviteHandler(webapp.RequestHandler):
	
	def get(self):
		currentGroup = Group.get("agZkZS1iZWVyCwsSBUdyb3VwGAEM")
		
		path = os.path.join(os.path.dirname(__file__), 'enterInvite.html')
		self.response.out.write(template.render(path, 
			{
			'group': currentGroup
			}))