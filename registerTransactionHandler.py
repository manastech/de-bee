import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template
from mail_handler import *
from mail_sender import *
from serverUtils import UrlBuilder
from ajaxUtilities import alertMessage
from ajaxUtilities import redirectPage
from ajaxUtilities import authenticatedUser

class RegisterTransactionHandler(webapp.RequestHandler):
	
	def post(self):
		rejectPath = UrlBuilder(self.request).buildUrl('/reject')
		
		group = Group.get(self.request.get('group'))
		creator = users.get_current_user();
		fromUser = users.User(self.request.get('fromUser'))
		toUser = users.User(self.request.get('toUser'));
		try:
		  amount = float(self.request.get('amount'))
		except BaseException, e:
			error = 'Invalid amount: %s.' % self.request.get('amount')
			alertMessage(self, error)
			return
		
		reason = self.request.get('reason')
		type = self.request.get('type')
		
		if amount <= 0:
			error = 'Invalid amount: %s.' % amount
			alertMessage(self, error)
			return
		
		tr = Transaction(
			group = group,
			creator = creator, fromUser = fromUser, toUser = toUser,
			type = type,
			amount = amount, reason = reason,
			isRejected = False
			)
		tr.put()
				
		fromMembership = Membership.gql("WHERE user = :1 AND group = :2", fromUser, group).get()
		toMembership = Membership.gql("WHERE user = :1 AND group = :2", toUser, group).get()
		# TODO revisar
		if type == 'debt' or type == 'rejectedPayment':
			fromMembership.balance -= amount
			toMembership.balance += amount
			if(fromUser != creator):
				MailSender().sendTransactionNotice(fromUser.email(), fromMembership.name(), tr, rejectPath)
		elif type == 'payment' or type == 'rejectedDebt': 
			fromMembership.balance += amount
			toMembership.balance -= amount
			if(toUser != creator):
				MailSender().sendTransactionNotice(toUser.email(), toMembership.name(), tr, rejectPath)
				
		fromMembership.put()
		toMembership.put()
		
		location = '/group?group=%s' % group.key()
		redirectPage(self,location)
		 