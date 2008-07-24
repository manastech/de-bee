from google.appengine.api import mail
from groupInvitationHandler import GroupInvitation
from mail_handler import *

# TODO codigo duplicado
class TransactionHash:
	def validate(self, transaction, hash):
		realHash = self.makeHash(transaction)
		valid = hash == realHash
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
		
		
class MailSender:

	def sendInvitationMail(self,user_recipient, group, custom_invitation_text, urlBuilder):
		inv = GroupInvitation(group, user_recipient, urlBuilder)
		subject = "You are invited to %s group!" % group.name
		body = "click %s to accept. yeah! %s " % (inv.getUrl(), custom_invitation_text)
		mail.send_mail("de-bee@manas.com.ar", user_recipient, subject, body)

	def sendTransactionNotice(self, user_recipient, group_name, transaction, uri_reject_mail):
		subject = "Transaction notice in %s group" % group_name
		hasher = TransactionHash()
		hash = hasher.makeHash(transaction)
		
		if transaction.type == 'debt':
			body = "You owe %s $%s because of %s. If you want to reject the debt you can click %s ." \
			 	   % (transaction.toUser, transaction.amount, transaction.reason,\
			 	   (uri_reject_mail + "?key=" + str(transaction.key()) +"&h=" +hash))
		elif transaction.type == 'payment':
			body = "%s payed you $%s because of %s. If you want to reject the payment you can click %s ." \
			 	   % (transaction.fromUser, transaction.amount, transaction.reason,\
			 	   (uri_reject_mail + "?key=" + str(transaction.key()) +"&h=" +hash))
			 	   
		mail.send_mail("de-bee@manas.com.ar", user_recipient, subject, body)
        
