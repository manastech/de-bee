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

	def sendInvitationMail(self, user_sender, user_recipient, group, custom_invitation_text, urlBuilder):
		inv = GroupInvitation(group, user_recipient, urlBuilder)
		plainUrl = inv.getUrl()
		fancyUrl = '<a href="%s">here</a>' % plainUrl
		subject = "De-Bee: You are invited to %s group!" % group.name
		
		message = mail.EmailMessage(sender="info@de-bee.com", to=user_recipient, subject=subject)
		
		if len(custom_invitation_text) > 0:
			plainInvitationText = custom_invitation_text + '\n\n'
			fancyInvitationText = custom_invitation_text + '<br><br>'
		else:
			plainInvitationText = ''
			fancyInvitationText = ''
		
		message.body = 'Hello %s!\n\n' \
		'%s has invited you to join %s group in De-Bee.\n\n' \
		'%s' \
		'To sign up please copy and paste this link in your browser: %s\n\n' \
		'De-Bee gives you a new way to deal with money change and debts.\n' \
		'Any exchange money situation with friends or any acquaintance can be resolved with De-Bee.\n\n' \
		'You can:\n\n' \
		'*  Create groups and invite your friends to join them.\n' \
		'*  Join other groups your friends had invited you to.\n\n' \
		'De-Bee is totally secure. No one can fool you assigning you a debt without your consent.\n\n' \
		'There are four common actions you will use:\n\n' \
		'* Register a payment you have made to someone\n' \
		'* Register a debt you have with someone\n' \
		'* Register a payment someone has made to you\n' \
		'* Register a debt someone has with you\n\n' \
		'De-Bee informs you about your summarized situation for all your groups and for each group in particular.\n\n\n' \
		'Thanks,\n\nDe-Bee' \
		% (user_recipient, user_sender, group.name, plainInvitationText, plainUrl )
		
		message.html = 'Hello %s!<br><br>' \
		'%s has invited you to join %s group in De-Bee.<br><br>' \
		'%s' \
		'To sign up please click %s<br><br>' \
		'De-Bee gives you a new way to deal with money change and debts.<br>' \
		'Any exchange money situation with friends or any acquaintance can be resolved with De-Bee.<br><br>' \
		'You can:<br><br><ul>' \
		'<li>Create groups and invite your friends to join them.</li>' \
		'<li>Join other groups your friends had invited you to.</li></ul><br>' \
		'De-Bee is totally secure. No one can fool you assigning you a debt without your consent.<br><br>' \
		'There are four common actions you will use:<br><br><ul>' \
		'<li>Register a payment you have made to someone</li>' \
		'<li>Register a debt you have with someone</li>' \
		'<li>Register a payment someone has made to you</li>' \
		'<li>Register a debt someone has with you</li></ul><br>' \
		'De-bee informs you about your summarized situation for all your groups and for each group in particular.<br><br><br>' \
		'Thanks,<br><br>De-Bee' \
		% (user_recipient, user_sender, group.name, fancyInvitationText, fancyUrl )
		
		message.send()

	def sendTransactionNotice(self, user_recipient, group_name, transaction, uri_reject_mail):
		subject = "De-Bee: Transaction notice in %s group" % group_name 
		hasher = TransactionHash()
		hash = hasher.makeHash(transaction)
		url = uri_reject_mail + "?key=" + str(transaction.key()) +"&h=" + hash
		fancyUrl = '<a href="%s">here</a>' % url
		
		message = mail.EmailMessage(sender="info@de-bee.com", to=user_recipient, subject=subject)

		if transaction.type == 'debt':
			if transaction.creator == transaction.toUser:
				message.body = 'Hi %s!\n\n' \
				'%s told us that you owe him/her $%s because of %s.\n' \
				'If you do not owe this money you can reject the debt, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\n\e-Bee' \
				% (transaction.fromUser, transaction.toUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>you owe him/her $%s</b> because of %s.<br>' \
				'If you do not owe this money you can reject the debt clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.fromUser, transaction.toUser, transaction.amount, transaction.reason, fancyUrl)
			elif transaction.creator == transaction.fromUser:
				message.body = 'Hi %s!\n\n' \
				'%s told us that he/she owes you $%s because of %s.\n' \
				'If he/she does not owe this money you can reject the debt, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.toUser, transaction.fromUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>he/she owes you $%s</b> because of %s.<br>' \
				'If he/she does not owe this money you can reject the debt clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.toUser, transaction.fromUser, transaction.amount, transaction.reason, fancyUrl)
			elif user_recipient == transaction.fromUser.email():
				message.body = 'Hi %s!\n\n' \
				'%s told us that you owe %s $%s because of %s.\n' \
				'If you do not owe this money you can reject the debt, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.fromUser, transaction.creator, transaction.toUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>you owe %s $%s</b> because of %s.<br>' \
				'If you do not owe this money you can reject the debt clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.fromUser, transaction.creator, transaction.toUser, transaction.amount, transaction.reason, fancyUrl)
			elif user_recipient == transaction.toUser.email():
				message.body = 'Hi %s!\n\n' \
				'%s told us that %s owes you $%s because of %s.\n' \
				'If he/she does not owe this money you can reject the debt, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.toUser, transaction.creator, transaction.fromUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>%s owes you $%s</b> because of %s.<br>' \
				'If he/she does not owe this money you can reject the debt clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.toUser, transaction.creator, transaction.fromUser, transaction.amount, transaction.reason, fancyUrl)
		elif transaction.type == 'payment':
			if transaction.creator == transaction.fromUser:
				message.body = 'Hi %s!\n\n' \
				'%s told us that he/she payed you $%s because of %s.\n' \
				'If you did not get that money you can reject this, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.toUser, transaction.fromUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>he/she payed you $%s</b> because of %s.<br>' \
				'If you did not get that money you can reject this clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.toUser, transaction.fromUser, transaction.amount, transaction.reason, fancyUrl)
			elif transaction.creator == transaction.toUser:
				message.body = 'Hi %s!\n\n' \
				'%s told us that you payed him/her $%s because of %s.\n' \
				'If you did not get that money you can reject this, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.fromUser, transaction.toUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>you payed him/her $%s</b> because of %s.<br>' \
				'If you did not get that money you can reject this clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.fromUser, transaction.toUser, transaction.amount, transaction.reason, fancyUrl)
			elif user_recipient == transaction.toUser.email():
				message.body = 'Hi %s!\n\n' \
				'%s told us that %s payed you $%s because of %s.\n' \
				'If you did not get that money you can reject this, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.toUser, transaction.creator, transaction.fromUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>%s payed you $%s</b> because of %s.<br>' \
				'If you did not get that money you can reject this clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.toUser, transaction.creator, transaction.fromUser, transaction.amount, transaction.reason, fancyUrl)
			elif user_recipient == transaction.fromUser.email():
				message.body = 'Hi %s!\n\n' \
				'%s told us that you payed %s $%s because of %s.\n' \
				'If you did not payed that money you can reject this, please copy and paste this text in your browser: %s\n\n\n' \
				'Yours,\nDe-Bee' \
				% (transaction.fromUser, transaction.creator, transaction.toUser, transaction.amount, transaction.reason, url)
				
				message.html = 'Hi %s!<br><br>' \
				'<b>%s</b> told us that <b>you payed %s $%s</b> because of %s.<br>' \
				'If you did not payed that money you can reject this clicking %s.<br><br><br>' \
				'Yours,<br>De-Bee' \
				% (transaction.fromUser, transaction.creator, transaction.toUser, transaction.amount, transaction.reason, fancyUrl)
				
		message.send();
		
	def sendTransactionRejectNotice(self, user_recipient, group_name, transaction, reason):
		subject = "De-Bee: Transaction rejection notice in %s group" % group_name
		message = mail.EmailMessage(sender="info@de-bee.com", to=user_recipient, subject=subject)
		message.body = 'Hi %s!\n\n' % user_recipient
		message.html = 'Hi %s!<br><br>' % user_recipient
		
		if user_recipient == transaction.fromUser.email():
			msg = '%s has rejected a transaction saying that ' % transaction.toUser.nickname()
			msg += 'you '
			if transaction.type == 'debt':
				msg += 'owe '
			else:
				msg += 'payed '
			msg += 'him/her '
			
			message.body += msg
			message.html += msg
		else:
			msg = '%s has rejected a transaction saying that ' % transaction.fromUser.nickname()
			msg += 'he/she '
			if transaction.type == 'debt':
				msg += 'owes '
			else:
				msg += 'payed '
			msg += 'you '
			
			message.body += msg
			message.html += msg
		 
		message.body += '$%s because of %s\n\n' % (transaction.amount, transaction.reason)
		message.html += '$%s because of %s<br><br>' % (transaction.amount, transaction.reason)
		
		message.body += 'His/her reason is:\n\n%s\n\n' % reason
		message.html += 'His/her reason is:<br><br>%s<br><br>' % reason
		
		message.body += 'Yours,\nDe-Bee'
		message.html += 'Yours,<br>De-Bee'
		
		message.send();