import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

class GroupInvitationHandler(webapp.RequestHandler):
		
	def get(self):
		pass