from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from ajax import userIsLoggedIn
from ajax import alertMessage
from ajax import redirectPage
from model import Membership
from model import Transaction
from model import Group
from emails import DeBeeEmail
from emails import transactionNoticeSubject
from util import UrlBuilder
from util import readFile
from orderParser import OrderParser

class BulkHandler(webapp.RequestHandler):
	
	def post(self):
		if not userIsLoggedIn(self):
			return
			
		rejectPath = UrlBuilder(self.request).buildUrl('/reject')
		
		user = users.get_current_user();
		group = Group.get(self.request.get("group"))
		
		creatorMember = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
		if not creatorMember:
			return
		
		command = self.request.get("command")
		members = group.memberships
		
		parser = OrderParser()
		transaction = parser.parse(members, command)
		
		if transaction.error:
			alertMessage(self, transaction.error)
			return
		
		if creatorMember.user == transaction.payer.user:
			debtorMailTxt = readFile('texts/creator_payed_you.txt')
			debtorMailHtml = readFile('texts/creator_payed_you.html')
		else:
			debtorMailTxt = readFile('texts/creator_says_someone_payed_you.txt')
			debtorMailHtml = readFile('texts/creator_says_someone_payed_you.html')
		
		for debt in transaction.debts:
			debtor = debt.member
			payer = transaction.payer
			
			if debtor.user.email().lower() == payer.user.email().lower():
				continue
			
			# Adjust balance
			debtor.balance -= debt.money
			debtor.put()
			
			payer.balance += debt.money
			
			# Create rejected transaction
			tr = Transaction(
			    group = group,
			    creatorMember = creatorMember, 
			    fromMember = payer,
			    toMember = debtor,
			    type = 'payment',
			    amount = debt.money, 
			    reason = debt.reason,
			    isRejected = False
			    )
			tr.put()
			
			# If the one that created this transaction is the one that owes,
			# don't sent a mail to him/her
			if creatorMember.user == debtor.user:
				continue
			
			# Build the reject url
			rejectUrl = UrlBuilder(self.request).buildUrl('/reject')
			rejectUrl += "?key=%s&h=%s" % (str(tr.key()), tr.hash)
			
			# Try send email to the debtor
			message = mail.EmailMessage(
			                sender = DeBeeEmail,
			                to = debtor.user.email(), 
			                subject = transactionNoticeSubject(debtor))
			
			if creatorMember.user == transaction.payer.user:
				message.body = debtorMailTxt % (debtor.userNick, payer.userNick, debt.money, debt.reason, rejectUrl)
				message.html = debtorMailHtml % (debtor.userNick, payer.userNick, debt.money, debt.reason, rejectUrl)
			else:
				message.body = debtorMailTxt % (debtor.userNick, creatorMember.userNick, payer.userNick, debt.money, debt.reason, rejectUrl)
				message.html = debtorMailHtml % (debtor.userNick, creatorMember.userNick, payer.userNick, debt.money, debt.reason, rejectUrl)
				
			try:
				message.send()
			except:
				iHateGoogleAppEngineMailQuotaRules = True
				
		transaction.payer.put()
		
		# Now try send email to the payer with a summary
		if not creatorMember.user == transaction.payer.user:
			debtorsTxt = ''
			debtorsHtml = '<ul>'
			
			for debt in transaction.debts:
				debtorsTxt += ' * $%s to %s because of %s\n' % (debt.money, debt.member.userNick, debt.reason)
				debtorsHtml += '<li>$%s to %s because of %s</li>' % (debt.money, debt.member.userNick, debt.reason)
				
			debtorsHtml += '</ul>'
			
			# Try send email to the debtor
			message = mail.EmailMessage(
			                sender = DeBeeEmail,
			                to = transaction.payer.user.email(), 
			                subject = transactionNoticeSubject(transaction.payer))
			
			message.body = readFile('texts/creator_says_you_payed_for_them.txt') % (transaction.payer.userNick, creatorMember.userNick, debtorsTxt)
			message.html = readFile('texts/creator_says_you_payed_for_them.html') % (transaction.payer.userNick, creatorMember.userNick, debtorsHtml)
			
			try:
				message.send()
			except:
				iHateGoogleAppEngineMailQuotaRules = True
				
		location = '/group?group=%s&msg=%s' % (group.key(), 'Debts saved!')
		redirectPage(self,location)