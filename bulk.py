import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from model import *
from google.appengine.api import users
import registration as registration
from serverUtils import UrlBuilder
from ajaxUtilities import alertMessage
from ajaxUtilities import redirectPage
from ajaxUtilities import authenticatedUser
import os
from google.appengine.ext.webapp import template
import time
import datetime
from orderParser import *
from registerTransactionHandler import *

class BulkDoHandler(webapp.RequestHandler):
	
	def post(self):
		if authenticatedUser(self):
			rejectPath = UrlBuilder(self.request).buildUrl('/reject')
			
			command = self.request.get("command")
			group = Group.get(self.request.get("group"))
			creator = users.get_current_user();
			members = Membership.gql("WHERE group = :1", group)
			members = members.fetch(10000)
			
			parser = OrderParser()
			transaction = parser.parse(members, command)
			
			if transaction.error:
				alertMessage(self, transaction.error)
				return
			
			for debt in transaction.debts:
				p1 = debt.member.user
				p2 = transaction.payer.user
				
				if p1.email().lower() == p2.email().lower():
					continue
				
				if transaction.cancel:
					registerTransaction(group, creator, p2, p1, debt.money, '(cancel) %s' % debt.reason, 'debt', rejectPath)
				else:
					registerTransaction(group, creator, p1, p2, debt.money, debt.reason, 'debt', rejectPath)
					
			location = '/group?group=%s&msg=%s' % (group.key(), 'Debts loaded!')
			redirectPage(self,location)

class BulkSummaryHandler(webapp.RequestHandler):
	
	@login_required
	def get(self):
		alertMessage(self, "Bulk summary!")		