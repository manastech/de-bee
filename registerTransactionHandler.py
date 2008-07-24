import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

class RegisterTransactionHandler(webapp.RequestHandler):
	
	def post(self):
		self.response.out.write('<html><body><pre>')
		self.response.out.write(cgi.escape(self.request.get('fromUser')))
		self.response.out.write(' owes ')
		self.response.out.write(cgi.escape(self.request.get('amount')))
		self.response.out.write(' to ')
		self.response.out.write(cgi.escape(self.request.get('toUser')))
		self.response.out.write(' because of ')
		self.response.out.write(cgi.escape(self.request.get('reason')))
		self.response.out.write('</pre></body></html>')