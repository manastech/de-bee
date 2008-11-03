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
from orderParser import OrderParser
from orderParser import quantity
from i18n import getLanguage
from i18n import _

class BulkHandler(webapp.RequestHandler):
	
	def post(self):
		if not userIsLoggedIn(self):
			return
			
		rejectPath = UrlBuilder(self.request).buildUrl('/reject')
		
		user = users.get_current_user()
		lang = getLanguage(self, user)
		group = Group.get(self.request.get("group"))
		
		creatorMember = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
		if not creatorMember:
			return
		
		command = self.request.get("command")
		members = group.memberships
		
		parser = OrderParser()
		parser.lang = lang
		transaction = parser.parse(members, command)
		
		if transaction.error:
			alertMessage(self, transaction.error)
			return
			
		payersBalanceBefore = transaction.payer.balance
		
		for debt in transaction.debts:
		    debtor = debt.member
		    payer = transaction.payer
		    debtorLang = getLanguage(self, debtor.user)
			
		    if debtor.user.email().lower() == payer.user.email().lower():
		        continue
			
		    debtorsBalanceBefore = debtor.balance
		    
		    # Adjust balance
		    debtor.balance -= debt.money
		    debtor.put()
		    
		    payer.balance += debt.money
		    
		    debtorsBalanceNow = debtor.balance
		    
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
		    	message = createActionMail(payer, debtor, debt.money, debt.reason, debtorsBalanceBefore, debtorsBalanceNow, rejectUrl, youOwedSomeone(debtorLang), debtorLang) 
		    else:
		    	message = createThirdPartyActionMail(creatorMember, payer, debtor, debt.money, debt.reason, debtorsBalanceBefore, debtorsBalanceNow, rejectUrl, creatorSaysYouOwedSomeone(debtorLang), debtorLang)
		    
		    sendEmail(message)
				
		transaction.payer.put()
		
		payersBalanceNow = transaction.payer.balance
		
		# Now try send email to the payer with a summary
		if not creatorMember.user == transaction.payer.user:
		    creatorLang = getLanguage(self, creatorMember.user)
		    message = createBulkMail(transaction, creatorMember, payersBalanceBefore, payersBalanceNow, creatorLang)
		    sendEmail(message)
				
		location = '/group?group=%s&msg=%s' % (group.key(), 'Debts saved!')
		redirectPage(self,location)
		
class BulkSummaryHandler(webapp.RequestHandler):
	
	def post(self):
		if not userIsLoggedIn(self):
			return
			
		user = users.get_current_user();
		lang = getLanguage(self, user)
		group = Group.get(self.request.get("group"))
		
		creatorMember = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
		if not creatorMember:
			return
		
		command = self.request.get("command")
		members = group.memberships
		
		parser = OrderParser()
		parser.lang = lang
		transaction = parser.parse(members, command)
		
		if transaction.error:
			alertMessage(self, transaction.error)
			return
		
		elems = {}
		total = 0.0
		
		for debt in transaction.debts:
			total += debt.money
			razon = debt.reason
			comidas = razon.split(',')
			for comida in comidas:
				comida = comida.strip()
				[cantidad, comida2] = quantity(comida)
				elems[comida2] = elems.get(comida2, 0) + cantidad
				
		result = ''
		for comida, cantidad in elems.items():
			result += ' - %s %s\\n' % (cantidad, comida)
			
		result += '\\n';
		result += _('Total', lang)
		result += ': $%s'% total;
		
		alertMessage(self, result)