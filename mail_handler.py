from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from hashlib import *
from mail_sender import *
from model import *

class MailHandler(webapp.RequestHandler):

	def get(self):
		mail_sender = MailSender()
		mail_sender.sendInvitationMail("jorge@manas.com.ar", "el nombre del grupo", "estas invitado che!","http://localhost:8080/reject")
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
			self.response.out.write("Something goes wrong")
			return
		
		transaction = Transaction.get(key)
		#transaction exists ?
		if(transaction is None):
			self.response.out.write("Something goes wrong")
			return
		
		#validate hash
		valid = TransactionHash().validate(transaction, hash)
		
		if valid :
			transaction.is_rejected = True
			new_transaction = createCompensateTransaction(transaction)
			new_transaction.put()
			transaction.put()
			self.response.out.write("ok!")
		else:
			self.response.out.write("Something goes wrong")

	def createCompensateTransaction(self, transaction):
		comp_type = None
		if transaction.type == "payment":
			comp_type = "rejectedPayment"
		elif transaction.type == "debt":
			comp_type = "rejectedDebt"
		
		new_transaction = Transaction(creator = transaction.creator,
									fromUser = transaction.fromUser, toUser = transaction.toUser,
									type = comp_type, amount = transaction.amount,
									isRejected = False)
		return new_transaction
		

class TransactionHash:
	def validate(self, transaction, hash):
		realHash = self.makeHash(transaction)
		valid = hash == realHash
		return valid
		
	def makeHash(self, transaction):
		m = sha224()
		m.update(transaction.key())
		m.update(transaction.creator)
		m.update(transaction.fromUser)
		m.update(transaction.toUser)
		m.update(transaction.type)
		m.update(transaction.date)
		return m.hexdigest()
		