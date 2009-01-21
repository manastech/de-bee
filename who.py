from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler
from model import Membership
from model import Group

class WhoHandler(webapp.RequestHandler):
	
	def get(self):
		page = self.request.get('p');
		if page is None or page == '':
			page = 1
		else:
			page = int(page)
			
		offset = (page - 1) * 10
		
		if page != 1:
			self.response.out.write("<a href=\"?p=%s\">Previous</a> | " % (page - 1))
			
		self.response.out.write(" &nbsp; %s &nbsp; " % page)
			
		self.response.out.write(" | <a href=\"?p=%s\">Next</a>" % (page + 1))
		
		self.response.out.write("<br/><br/>")
		
		for group in Group.gql("LIMIT %s, %s" % (offset, 10)):
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