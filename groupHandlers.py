import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template

def authenticatedUser(req):
	user = users.get_current_user()
	if user is not None:
		return True
	else:
		req.response.out.write("""
      <html>
        <body>
		You must logging first.
        </body>
      </html>""")
		return False

class GroupHandler(webapp.RequestHandler):
	
	def get(self):
		# Get user, group and me
		user = users.get_current_user()
		group = Group.get(self.request.get("group"))
		me = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
		
		# Calculate how much I owe or they owe me
		if me.balance != 0:
			if me.balance > 0:
				members = Membership.gql("WHERE group = :1 AND balance < 0 ORDER BY balance", group)
				sign = 1
			else:
				members = Membership.gql("WHERE group = :1 AND balance > 0 ORDER BY balance DESC", group)
				sign = -1
			
			balance = me.balance * sign
			result = []
			
			for member in members:
				if balance <= 0:
					break
				result.append({'user': member.user, 'amount': min(balance, member.balance * -sign)})
				balance -= member.balance * -sign
		else:
			sign = 0
			result = []
			
		# Get transaction history
		# TODO filtrar por grupo y por mi!
		try:
			transactionCount = int(self.request.get('transactionCount', default_value="0"))
			transactions_query = Transaction.all().order('-date')
			transactions = transactions_query.fetch(transactionCount)
			validationError = False
			validationMessage = ''
			
		except BaseException, e:
			transactionCount = 0
			transactions = []
			validationError = True
			validationMessage = '(This should be a number)'
			
		# Get all members
		members = Membership.gql("WHERE user != :1 AND group = :2", user, group)
		
		template_values = {
			'balance': me.balance * sign,
			'balancePositive': sign > 0,
			'balanceIsZero': sign == 0,
			'result': result,
			'currentUser': user,
			'members': members, 
			'group': group,
			'transactionCount': transactionCount,
			'transactions': transactions,
			'validationError': validationError,
			'validationMessage': validationMessage
			 }
		
		path = os.path.join(os.path.dirname(__file__), 'group.html')
		self.response.out.write(template.render(path, template_values))

class GroupCreationHandler(webapp.RequestHandler):

	def post(self):
		registered = authenticatedUser(self)
		if registered:
			groupName = self.request.get('name')
			escapedGroupName = cgi.escape(groupName)

			if groupName == "":
				self.response.out.write('<html><body><pre>')
				self.response.out.write("Group name is required. <a href='javascript:history.back()'>Go back</a>.")
				self.response.out.write('</pre></body></html>')
			else:
				group = self.createGroupAndInsertMember(groupName)

				if group is None:
					self.response.out.write('<html><body><pre>')
					self.response.out.write("The group " + escapedGroupName + " already exists. Please try another name. <a href='javascript:history.back()'>Go back</a>.")
					self.response.out.write('</pre></body></html>')
				else:
					self.redirect("/group?group=%s" % group.key())

	def insertUserInGroup(self, group):
		membership = Membership(user=users.get_current_user(),group=group,balance=0.0)
		membership.put()

	def createGroupAndInsertMember(self, gname):
		query = Group.gql("WHERE name = :1", gname)
		count = query.count()
		if count > 0:
			return None
		group = Group(name=gname)
		group.put()
    	
		self.insertUserInGroup(group)
		return group
