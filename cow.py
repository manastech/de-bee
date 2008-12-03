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
		msg += ': $%s\\n\\n'% result.each;
		
		for debt in result.debts:
			i = 0
			for singleDebt in debt.singleDebts:
				if i == 0:
					msg += _('%(from)s owes %(to)s $%(amount)s', lang) % { 'from': debt.fromMember.userNick, 'to': singleDebt.toMember.userNick, 'amount': singleDebt.money }
				elif i < len(debt.singleDebts) - 1:
					msg += ', '
					msg += _('%(to)s $%(amount)s', lang) % { 'to': singleDebt.toMember.userNick, 'amount': singleDebt.money }
				else:
					msg += ' '
					msg += _('and', lang)
					msg += ' '
					msg += _('%(to)s $%(amount)s', lang) % { 'from': debt.fromMember.userNick, 'to': singleDebt.toMember.userNick, 'amount': singleDebt.money }
				msg += '\\n'
				i = i + 1
			
		alertMessage(self, msg)