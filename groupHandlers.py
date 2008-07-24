import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration

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

class EnterGroupCreationHandler(webapp.RequestHandler):
	
	def get(self):
    		registered = authenticatedUser(self)
		if registered:
			self.response.out.write("""
      <html>
        <body>
          <form action="/groupCreation" method="post">
          	<div>Name: <input type="text" value="group name" name="name"/></div>
            <div><input type="submit" value="Create"></div>
          </form>
        </body>
      </html>""")
			

class GroupCreationHandler(webapp.RequestHandler):

	def post(self):
		
    		registered = authenticatedUser(self)
		if registered:
			self.response.out.write('<html><body><pre>')
			groupName = self.request.get('name')
			escapedGroupName = cgi.escape(groupName)

			if groupName == "":
				self.response.out.write("Group name is required")
			else:
				group = self.createGroupAndInsertMember(groupName)

				if group is None:
					self.response.out.write("The group " + escapedGroupName + " already exists. Please try another name.")
				else:
					self.response.out.write("The group " + escapedGroupName + " has been created.")
			self.response.out.write('</pre></body></html>')

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
