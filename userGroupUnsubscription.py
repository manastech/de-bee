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
    		registered = authenticatedUser(self)
    		
		if registered:
			registered = users.get_current_user()
			
			self.response.out.write('<html><body><pre>')
			groupKey = self.request.get('group')
			
			if groupKey == "":
				self.response.out.write("Group is required")
			else:
                                group = Group.get(groupKey)
                                memberships = Membership.gql("WHERE group = :1 AND user = :2", group, registered)

                                if memberships.count() <> 1:
					self.response.out.write("You are not registered in this group")
				else:
                                        membership = memberships.get()
                                        if not membership.balance == 0.0:
                                                self.response.out.write("You cannot leave this group")
                                        else:
											membership.delete()
											if Membership.gql("WHERE group = :1", group).count() == 0:
												group.delete()
											self.response.out.write("You have been unsubscribed from the group " + cgi.escape(group.name))
			self.response.out.write('</pre></body></html>')
