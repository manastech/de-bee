import cgi
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from model import *
from google.appengine.api import users
import registration as registration
from ajaxUtilities import alertMessage
from ajaxUtilities import redirectPage
from ajaxUtilities import authenticatedUser
import os
from google.appengine.ext.webapp import template
import time
import datetime

class GroupHandler(webapp.RequestHandler):
	
	@login_required
	def get(self):
		# Get user, group and me
		user = users.get_current_user()
		group = Group.get(self.request.get("group"))
		goToHistoryTab = self.request.get("goToHistoryTab")
		me = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
		
		# Calculate how much I owe or they owe me
		if me.balance != 0.0:
			if me.balance > 0.0:
				members = Membership.gql("WHERE group = :1 AND balance < 0.0 ORDER BY balance", group)
				sign = 1
			else:
				members = Membership.gql("WHERE group = :1 AND balance > 0.0 ORDER BY balance DESC", group)
				sign = -1
			
			balance = me.balance * sign
			result = []
			
			for member in members:
				if balance <= 0.0:
					break
				result.append({'user': member.nick, 'amount': min(balance, member.balance * -sign)})
				balance -= member.balance * -sign
		else:
			sign = 0
			result = []
			
		# Get transaction history
		# TODO filtrar por grupo y por mi!
		try:
			transactionCount = int(self.request.get('transactionCount', default_value=10))
			
			transactions_query_from = Transaction.gql("WHERE group = :1 AND fromMember = :2 ORDER BY date DESC", group, me)
			transactions_from = transactions_query_from.fetch(transactionCount)
			
			transactions_query_to = Transaction.gql("WHERE group = :1 AND toMember = :2 ORDER BY date DESC", group, me)
			transactions_to = transactions_query_to.fetch(transactionCount)
			
			transactions = transactions_from + transactions_to
			transactions.sort(cmp = compareTransactionsByDate)
			
			transactions = transactions[0:transactionCount]
			
			messages = []
			for tr in transactions:
				if not tr.fromUser or not tr.toUser or not tr.creator:
					continue
				
				if (tr.type == "debt"):
			 		if (tr.fromUser == user):
			 			message = "<span style=\"color:#5C0101\">You owed " + tr.toMember.nick + " $" + str(tr.amount)
			 		else:
			 			message = "<span style=\"color:#005E00\">" + tr.fromMember.nick + " owed you $" + str(tr.amount)
			 	if (tr.type == "payment"):
			 		if (tr.fromUser == user):
			 			message = "<span style=\"color:#005E00\">You payed " + tr.toMember.nick + " $" + str(tr.amount)
			 		else:
			 			message = "<span style=\"color:#5C0101\">" + tr.fromMember.nick + " payed you $" + str(tr.amount)
			 	if (tr.type == "rejectedDebt"):
			 		if (tr.fromUser == user):
			 			message = "<span style=\"color:#005E00\">You rejected from " + tr.toMember.nick + " a debt of $" + str(tr.amount)
			 		else:
			 			message = "<span style=\"color:#5C0101\">" + tr.fromMember.nick + " rejected you a debt of $" + str(tr.amount)
			 	if (tr.type == "rejectedPayment"):
			 		if (tr.fromUser == user):
			 			message = "<span style=\"color:#005E00\">You rejected from " + tr.toMember.nick + " a payment of $" + str(tr.amount)
			 		else:
			 			message = "<span style=\"color:#5C0101\">" + tr.fromMember.nick + " rejected you a payment of $" + str(tr.amount)
			 	if ( len(tr.reason) > 0 ):
			 		message = message + " due to " + tr.reason + "</span>"
			 	message = niceDate(tr.date) + " " + message
			 	messages.append(message)
			 	
			transactions = messages
			
			validationError = False
			validationMessage = ''
			
		except BaseException, e:
			transactionCount = 0
			transactions = []
			validationError = True
			validationMessage = '(This should be a number)'
			
		# Get all members
		members = Membership.gql("WHERE user != :1 AND group = :2", user, group)
		members = members.fetch(100000)
		
		hasMembers = len(members) > 0
		
		memberships = self.getMemberships(user)
		hasMemberships = len(memberships) > 0

		# Get group balance
		debtors = Membership.gql("WHERE group = :1 AND balance < 0.0 ORDER BY balance", group)
		creditors = Membership.gql("WHERE group = :1 AND balance > 0.0 ORDER BY balance", group)

		groupDebtors = []
		for member in debtors:
			groupDebtors.append({'user': member.nick, 'amount': member.balance*-1})
		
		groupCreditors = []
		for member in creditors:
			groupCreditors.append({'user': member.nick, 'amount': member.balance})
			
		autocompleteMembers = "";
		for member in members:
			autocompleteMembers += "'" + member.nick + "'"
			autocompleteMembers += ", "
		autocompleteMembers += "'" + me.nick + "'"
		
		template_values = {
			'balance': me.balance * sign,
			'balancePositive': sign > 0,
			'balanceIsZero': sign == 0,
			'result': result,
			'currentUser': user,
			'members': members,
			'hasMembers': hasMembers,
			'membership': me,
			'hasTransactions': len(transactions) > 0,
			'transactionCount': transactionCount,
			'transactions': transactions,
			'validationError': validationError,
			'validationMessage': validationMessage,
			'memberships': self.getMemberships(user),
			'hasMemberships': hasMemberships,
			'message': self.request.get("msg"),
			'goToHistoryTab': goToHistoryTab, 
			'signout_url': users.create_logout_url("/"),
			'hasMoreThanOneItem': len(result) > 1,
			'groupDebtors': groupDebtors,
			'hasDebtors': len(groupDebtors) > 0,
			'groupCreditors': groupCreditors,
			'hasCreditors': len(groupCreditors) > 0,
			'autocompleteMembers': autocompleteMembers
			 }
		
		path = os.path.join(os.path.dirname(__file__), 'group.html')
		self.response.out.write(template.render(path, template_values))
	
	def getMemberships(self, user):
		actualGroup = Group.get(self.request.get("group"))
		memberships = Membership.gql("WHERE user = :1 AND group != :2", user, actualGroup)
		memberships = memberships.fetch(100000)
		return memberships
		
def compareTransactionsByDate(x, y):
	if x.date > y.date:
		return -1
	elif x.date < y.date:
	 	return 1
	else:
		return 0
	
def niceDate(t):
	now = datetime.datetime.now()
	if now.year == t.year:
		if now.month == t.month and now.day == t.day:
			return t.strftime("Today at %H:%S")
		return t.strftime("On %b %d")
	else:
		return t.strftime("On %D")

class GroupCreationHandler(webapp.RequestHandler):
	
	def post(self):
		if authenticatedUser(self):
			groupName = self.request.get('name').strip()
			escapedGroupName = cgi.escape(groupName)
	
			if groupName == "": # verificar que el nombre no sea vacio
				error = 'Group name is required.'
				alertMessage(self,error)
				return
			else:
				group = self.createGroupAndInsertMember(groupName)
	
				if group is None: # si el usuario es miembro de un grupo con alias igual al nombre del grupo que quiere crear, no dejarlo
					error = 'You already have a group with the name ' + escapedGroupName + '. Please try another name.'
					alertMessage(self,error)
				else: # si esta todo ok, se creo el grupo, redireccionarlo al detalle de ese grupo
					location = '/group?group=%s' % group.key()
					redirectPage(self,location)

	def insertUserInGroup(self, group):
		membership = Membership(user=users.get_current_user(),group=group,balance=0.0,alias=group.name)
		membership.put()

	def createGroupAndInsertMember(self, gname):
		user = users.get_current_user()
		count = Membership.gql("WHERE user = :1 AND alias = :2", user, gname).count()
		if count > 0:
			return None
		group = Group(name=gname)
		group.put()
    	
		self.insertUserInGroup(group)
		return group

class GroupChangeAliasHandler(webapp.RequestHandler):
	
	def post(self):
		if not authenticatedUser(self):
			return
			
		membership = Membership.get(self.request.get('membership'))
		
		# Verificar que la membership que se paso sea efectivamente del usuario
		if not self.isMember(membership):
			return
		
		newAlias = self.request.get('alias').strip()
		newNickname = self.request.get('nickname').strip()
		
		# Verificar que el alias no sea vacio
		if newAlias == "":
			error = 'The name by which you want to see this group is required.'
			alertMessage(self,error)
			return
		
		# Verificar que no exista un alias del usuario con el mismo nombre
		if self.isAliasTaken(newAlias, membership.group):
			error = 'You already have a Group with the selected name, please select another name.'
			alertMessage(self,error)
			return
		
		# Verificar que el nickname no sea vacio
		if newNickname == "":
			error = 'The name by which you want others to see you in this group is required.'
			alertMessage(self,error)
			return
		
		# Verificar que el nickname no este tomado
		for other in Membership.gql("WHERE group = :1 AND user != :2", membership.group, membership.user):
			if other.nick == newNickname:
				error = 'The name by which you want others to see you in this group is already used by another member.'
				alertMessage(self,error)
				return

		membership.alias = newAlias
		membership.nickname = newNickname
		membership.put()
		location = '/group?group=%s&msg=%s' % (membership.group.key(), 'Properties changed!')
		redirectPage(self,location)
		    
	def isMember(self,membership):
		user = users.get_current_user()
		return membership.user == user 
	
	def isAliasTaken(self, alias, group):
		user = users.get_current_user()
		return Membership.gql("WHERE user = :1 AND alias = :2 AND group != :3", user, alias, group).count() > 0
