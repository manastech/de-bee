from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from hashlib import *
from mail_sender import *
from model import *
from google.appengine.ext.webapp.util import login_required
from ajaxUtilities import alertMessage
from ajaxUtilities import redirectPage
from ajaxUtilities import authenticatedUser
import os

class RejectTransactionHandler(webapp.RequestHandler):
	
	@login_required
	def get(self):
		key = self.request.get('key')
		hash = self.request.get('h')
		
		#parameter reception validation
		if(key is not None and hash is not None):
			transaction = Transaction.get(key)
			
			#transaction exists ?
			if(transaction is not None):
				#validate hash
				valid = TransactionHash().validate(transaction, hash)
				
				if valid:
					user = users.get_current_user()
					
					if (transaction.fromUser == user or transaction.toUser):
						template_values = {
							'key' : key,
							'h' : hash,	
							'hasMembership' : True,
							'hasgroups' : True,
							'group' : transaction.group,
							'username' : user.nickname(),
						}
						
						path = os.path.join(os.path.dirname(__file__), 'reject.html')
						self.response.out.write(template.render(path, template_values))
						return
		
		# some validation has fail
		msg = 'An error has occurred. The transaction could not be rejected.'
		self.redirect('/?msg=%s' % msg)

class DoRejectTransactionHandler(webapp.RequestHandler):
	
	def post(self):
		if authenticatedUser(self):
			key = self.request.get('key')
			hash = self.request.get('h')
			reason = self.request.get('reason').strip()
			
			if not reason:
				alertMessage(self, "Please enter a reason")
				return
			
			#parameter reception validation
			if(key is not None and hash is not None):
				transaction = Transaction.get(key)
				
				#transaction exists ?
				if(transaction is not None):
					#validate hash
					valid = TransactionHash().validate(transaction, hash)
					
					if valid:
						user = users.get_current_user()
						
						if (transaction.fromUser == user or transaction.toUser):
						
							transaction.isRejected = True
							new_transaction = self.createCompensateTransaction(transaction)
							new_transaction.put()
							transaction.put()
							
							fromMembership = Membership.gql("WHERE user = :1 AND group = :2", new_transaction.fromUser, new_transaction.group).get()
							toMembership = Membership.gql("WHERE user = :1 AND group = :2", new_transaction.toUser, new_transaction.group).get()
							
							if new_transaction.type == 'rejectedPayment':
								fromMembership.balance += new_transaction.amount
								toMembership.balance -= new_transaction.amount
							elif new_transaction.type == 'rejectedDebt': 
								fromMembership.balance += new_transaction.amount
								toMembership.balance -= new_transaction.amount
							
							fromMembership.put()
							toMembership.put()
							
							if new_transaction.fromUser.email() != user.email():
								MailSender().sendTransactionRejectNotice(new_transaction.fromUser.email(), fromMembership.name(), transaction, reason)
							else:
								MailSender().sendTransactionRejectNotice(new_transaction.toUser.email(), fromMembership.name(), transaction, reason)
							
							msg = 'The transaction has been succesfully rejected!'
							redirectPage(self, '/group?group=%s&msg=%s' % (transaction.group.key(), msg))
							return
				
	def createCompensateTransaction(self, transaction):
		comp_type = None
		fromVar = transaction.fromUser
		toVar = transaction.toUser
		creatorVar = user = users.get_current_user()
		
		if transaction.type == "payment":
			comp_type = "rejectedPayment"
			fromVar = transaction.toUser
			toVar = transaction.fromUser
		elif transaction.type == "debt":
			comp_type = "rejectedDebt"
		
		new_transaction = Transaction(creator = creatorVar,
									fromUser = fromVar, toUser = toVar,
									type = comp_type, amount = transaction.amount,
									group = transaction.group,
									reason = transaction.reason,
									isRejected = False)
		return new_transaction


# TODO codigo duplicado
class TransactionHash:
	def validate(self, transaction, hash):
		realHash = self.makeHash(transaction)
		valid = (hash == realHash) and (not transaction.isRejected)
		return valid
		
	def makeHash(self, transaction):
		m = sha224()
		m.update(str(transaction.key()))
		m.update(transaction.creator.email())
		m.update(transaction.fromUser.email())
		m.update(transaction.toUser.email())
		m.update(transaction.type)
		m.update(str(transaction.date))
		return m.hexdigest()
	