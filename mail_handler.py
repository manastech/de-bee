from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from model import *
from mail_sender import *
from hashlib import *

class MailHandler(webapp.RequestHandler):

	def get(self):
		mail_sender = MailSender()
		mail_sender.sendInvitationMail("jorge@manas.com.ar", "el nombre del grupo", "estas invitado che!")
		mail_sender.sendNoticeTransaction("jonat@manas.com.ar", "jorge@manas.com.ar", "un grupo", None)
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
			self.redirect('/')
		
		transaction = Transaction.get(key)
		#transaction exists ?
		if(transaction is None):
			self.redirect('/')
		
		#validate hash
		valid = TransactionHash().validate(transaction, hash)
		
		if valid :
			
			transaction.is_rejected = True
			new_transaction = createCompensateTransaction(transaction)
			new_transaction.put()
			transaction.put()

	def createCompensateTransaction(self,transaction):
		pass
		
		
class TransactionHash():
	def validate(transaction, hash):
		realHash = self.makeHash(transaction)
		valid = hash == realHash
		
	def makeHash(transaction):
		m = sha224()
		m.update(transaction.key())
		m.update(transaction.creator)
		m.update(transaction.fromUser)
		m.update(transaction.toUser)
		m.update(transaction.type)
		m.update(transaction.date)
		return m.hexdigest()
		