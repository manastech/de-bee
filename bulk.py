from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from ajax import userIsLoggedIn
from ajax import alertMessage
from ajax import redirectPage
from model import Membership
from model import Transaction
from model import Group
from emails import youOwedSomeone
from emails import creatorSaysYouOwedSomeone
from emails import createActionMail
from emails import createThirdPartyActionMail
from emails import createBulkMail
from emails import sendEmail
from util import UrlBuilder
from util import descriptionOfBalance
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
			
		descriptionOfPayersBalanceBefore = descriptionOfBalance(transaction.payer, before = True)
		
		for debt in transaction.debts:
			debtor = debt.member
			payer = transaction.payer
			
			if debtor.user.email().lower() == payer.user.email().lower():
				continue
			
			descriptionOfDebtorsBalanceBefore = descriptionOfBalance(debtor, before = True)
			
			# Adjust balance
			debtor.balance -= debt.money
			debtor.put()
			
			payer.balance += debt.money
			
			descriptionOfDebtorsBalanceNow = descriptionOfBalance(debtor, before = False)
			
			# Create transaction
			tr = Transaction(
			    group = group,
			    creatorMember = creatorMember, 
			    fromMember = debtor,
			    toMember = payer,
			    type = 'debt',
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
			if creatorMember.user == transaction.payer.user:
				message = createActionMail(payer, debtor, debt.money, debt.reason, descriptionOfDebtorsBalanceBefore, descriptionOfDebtorsBalanceNow, rejectUrl, youOwedSomeone()) 
			else:
				message = createThirdPartyActionMail(creatorMember, payer, debtor, debt.money, debt.reason, descriptionOfDebtorsBalanceBefore, descriptionOfDebtorsBalanceNow, rejectUrl, creatorSaysYouOwedSomeone())
			
			sendEmail(message)
				
		transaction.payer.put()
		
		descriptionOfPayersBalanceNow = descriptionOfBalance(transaction.payer, before = False)
		
		# Now try send email to the payer with a summary
		if not creatorMember.user == transaction.payer.user:
			message = createBulkMail(transaction, creatorMember, descriptionOfPayersBalanceBefore, descriptionOfPayersBalanceNow)
			sendEmail(message)
				
		location = '/group?group=%s&msg=%s' % (group.key(), 'Debts saved!')
		redirectPage(self,location)