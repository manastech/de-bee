import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration
import os
from google.appengine.ext.webapp import template
from ajaxUtilities import alertMessage
from ajaxUtilities import redirectPage
from ajaxUtilities import authenticatedUser

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

class EnterUnsubscriptionHandler(webapp.RequestHandler):
	
	def get(self):
    		registered = authenticatedUser(self)
		if registered:
                        groups = self.groupsWithBalanceZero()        
			path = os.path.join(os.path.dirname(__file__), 'enterGroupUnsubscription.html')
                        self.response.out.write(template.render(path, 
			{
			'groups': groups
                        }))

        def groupsWithBalanceZero(self):
                memberships = Membership.gql("WHERE balance = 0.0")
                groups = []
                for membership in memberships:
                        groups.append(membership.group)
                
		return groups

class UnsubscriptionHandler(webapp.RequestHandler):

	def post(self):
		if authenticatedUser(self):
			user = users.get_current_user()
			
			groupKey = self.request.get('group').strip()
			
			if groupKey == "":
				error = 'Group is required'
				alertMessage(self,error)
				return
			else:
				group = Group.get(groupKey)
                memberships = Membership.gql("WHERE group = :1 AND user = :2", group, user)

                if memberships.count() <> 1:
                	error = 'You are not registered in this group.'
                	alertMessage(self,error)
                	return
                else:
					membership = memberships.get()
					if not membership.balance == 0.0:
						error = 'You cannot leave this group, your balance must be zero.'
						alertMessage(self,error)
						return
					else:
						membership.delete()
						if Membership.gql("WHERE group = :1", group).count() == 0:
							group.delete()
						
						msg = 'You have been succesfully unsubscribed from the group ' + cgi.escape(group.name) + '!'
						location = '/?msg=' + msg
						redirectPage(self,location)
