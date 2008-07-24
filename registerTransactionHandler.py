import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

class RegisterTransactionHandler(webapp.RequestHandler):
	
	def post(self):
		group = Group.get(self.request.get('group'))
		creator = users.get_current_user();
		fromUser = users.User(self.request.get('fromUser'))
		toUser = users.User(self.request.get('toUser'));
		try:
		  amount = float(self.request.get('amount'))
		except BaseException, e:
			self.response.out.write("Invalid amount: %s" % self.request.get('amount'))
			return
		reason = self.request.get('reason')
		type = self.request.get('type')
		
		if amount <= 0:
			self.response.out.write("Invalid amount: %s" % amount)
			return
		
		tr = Transaction(
			group = group,
			creator = creator, fromUser = fromUser, toUser = toUser,
			type = type,
			amount = amount, reason = reason,
			isRejected = False
			)
		tr.put()
		
		fromMembership = db.Query(Membership)
		fromMembership.filter('user = ', fromUser) 
		fromMembership.filter('group = ', group)
		fromMembership = fromMembership.get()
		
		toMembership = db.Query(Membership)
		toMembership.filter('user = ', toUser) 
		toMembership.filter('group = ', group)
		toMembership = toMembership.get()
		
		if type == 'debt' or type == 'rejectedPayment':
			fromMembership.balance -= amount
			toMembership.balance += amount
		elif type == 'payment' or type == 'rejectedDebt': 
			fromMembership.balance += amount
			toMembership.balance -= amount
			
		fromMembership.put()
		toMembership.put()
		
		self.response.out.write("Todo bien!")
		 