from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler
from model import Membership
from model import Group

class WhoHandler(webapp.RequestHandler):
	
	def get(self):
		for group in Group.all():
			self.response.out.write("<b>%s</b>" % group.name)
			
			self.response.out.write("<ul>")
			for membership in group.memberships:
				self.response.out.write("<li>%s (%s): $%s</li>" % (membership.userNick, membership.user.email(), membership.balance))
			self.response.out.write("</ul>")
			
def main():
    application = webapp.WSGIApplication([
                                        ('/who', WhoHandler),
                                        ], debug=True)
    
    CGIHandler().run(application)