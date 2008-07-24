from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from hashlib import *
from mail_sender import *
from model import *

class MailHandler(webapp.RequestHandler):

	def get(self):
		mail_sender = MailSender()
		mail_sender.sendInvitationMail("jorge@manas.com.ar", "el nombre del grupo", "estas invitado che!", "http://localhost:8080/reject")
		mail_sender.sendNoticeTransaction("jonat@manas.com.ar", "jorge@manas.com.ar", "un grupo", Transaction.get(""))
		self.response.out.write("""
			<html>
			<body>
			Ya lo mande
			</body>
			</html>""")


class RejectTransactionHandler(webapp.RequestHandler):

	def get(self):
		key = self.request.get('key')
		hash = self.request.get('h')
		
		#parameter reception validation
		if(key is None or hash is None):
			self.response.out.write("Parameters")
			return
		
		transaction = Transaction.get(key)
		#transaction exists ?
		if(transaction is None):
			self.response.out.write("No Transaction")
			return
		
		#validate hash
		valid = TransactionHash().validate(transaction, hash)
		
		if valid :
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
				fromMembership.balance -= new_transaction.amount
				toMembership.balance += new_transaction.amount
			
			fromMembership.put()
			toMembership.put()
			
			self.response.out.write("ok!")
		else:
			self.response.out.write("Is not valid")

	def createCompensateTransaction(self, transaction):
		comp_type = None
		fromVar = transaction.fromUser
		toVar = transaction.toUser
		creatorVar = transaction.toUser
		
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
	