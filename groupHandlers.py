import cgi
from google.appengine.ext import webapp
from model import *
from google.appengine.api import users
import registration as registration


class EnterGroupCreationHandler(webapp.RequestHandler):
	
	def get(self):
		self.response.out.write("""
      <html>
        <body>
          <form action="/createGroup" method="post">
          	<div>Name: <input type="text" value="group name" name="name"/></div>
            <div><input type="submit" value="Create"></div>
          </form>
        </body>
      </html>""")

class GroupCreationHandler(webapp.RequestHandler):

	def post(self):
		
		groupName = self.request.get('groupName')
		escapedGroupName = cgi.escape(groupName)
		group = create(groupName)

		self.response.out.write('<html><body><pre>')
		if group is None:
			self.response.out.write("The group " + escapedGroupName + " already exists. Please try another name.")
		else:
			self.response.out.write("The group " + escapedGroupName + " has been created.")
		self.response.out.write('</pre></body></html>')

	def create(name):
        	query = Group.gql("WHERE name = :1", name)
        	count = query.count()
        	if count > 0:
			return None
        	group = Group(name=name)
        	group.put()
        	return group
