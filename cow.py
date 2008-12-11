from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from ajax import userIsLoggedIn
from ajax import alertMessage
from ajax import redirectPage
from model import Membership
from model import Transaction
from model import Group
from emails import createCowMail
from emails import sendEmail
from util import UrlBuilder
from cowParser import CowParser
from cowParser import quantity
from i18n import getLanguage
from i18n import _

class CowHandler(webapp.RequestHandler):
	
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
		
		command = self.request.get("cow")
		members = group.memberships
		
		parser = CowParser()
		parser.lang = lang
		transaction = parser.parse(members, command)
		
		if transaction.error:
			alertMessage(self, transaction.error)
			return
		
		result = transaction.getResult()
		
		# Update balance and send mails
		for member, balance in result.balanceChange.iteritems():
			balanceBefore = member.balance
			balanceNow = member.balance + balance
			
			# Balance
			member.balance += balance
			member.put()
			
			# Send mail, but not to the creator of this mail
			if member.user != creatorMember.user:
				message = createCowMail(creatorMember, transaction, result, member, balanceBefore, balanceNow, lang)
				sendEmail(message)
			
		# Create transactions
		for debt in result.debts:
			for singleDebt in debt.singleDebts:
				tr = Transaction(
					group = group,
					creatorMember = creatorMember, 
					fromMember = debt.fromMember,
					toMember = singleDebt.toMember,
					type = 'debt',
					amount = singleDebt.money, 
					reason = transaction.reason,
					isRejected = False
				)
				tr.put()
				
		location = '/group?group=%s&msg=%s' % (group.key(), _('Debts saved!', lang))
		redirectPage(self,location)
		
class CowSummaryHandler(webapp.RequestHandler):
	
	def post(self):
		if not userIsLoggedIn(self):
			return
			
		user = users.get_current_user();
		lang = getLanguage(self, user)
		group = Group.get(self.request.get("group"))
		
		creatorMember = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
		if not creatorMember:
			return
		
		command = self.request.get("cow")
		members = group.memberships
		
		parser = CowParser()
		parser.lang = lang
		transaction = parser.parse(members, command)
		
		if transaction.error:
			alertMessage(self, transaction.error)
			return
		
		result = transaction.getResult()
		
		msg = ''
		msg += _('Total', lang)
		msg += ': $%s\\n'% result.total;
		msg += _('Each', lang)
		msg += ': $%s\\n\\n'% round(result.each, 2);
		
		for debt in result.debts:
			i = 0
			msg += ' - '
			for singleDebt in debt.singleDebts:
				tuple = { 'from': debt.fromMember.userNick, 'to': singleDebt.toMember.userNick, 'amount': round(singleDebt.money, 2) }
				if i == 0:
					if debt.fromMember.user == creatorMember.user:
						msg += _('You owe %(to)s $%(amount)s', lang) % tuple
					elif singleDebt.toMember.user == creatorMember.user:
						msg += _('%(from)s owes you $%(amount)s', lang) % tuple
					else:
						msg += _('%(from)s owes %(to)s $%(amount)s', lang) % tuple
				elif i < len(debt.singleDebts) - 1:
					msg += ', '
					if singleDebt.toMember.user == creatorMember.user:
						msg += _('you $%(amount)s', lang) % tuple
					else:
						msg += _('%(to)s $%(amount)s', lang) % tuple
				else:
					msg += ' '
					msg += _('and', lang)
					msg += ' '
					if singleDebt.toMember.user == creatorMember.user:
						msg += _('you $%(amount)s', lang) % tuple
					else:
						msg += _('%(to)s $%(amount)s', lang) % tuple
				i = i + 1
			msg += '\\n'
		
		alertMessage(self, msg)