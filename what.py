from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler
from model import Membership
from model import Group
from model import Transaction

class WhatHandler(webapp.RequestHandler):
	
	def get(self):
		page = self.request.get('p');
		if page is None or page == '':
			page = 1
		else:
			page = int(page)
			
		offset = (page - 1) * 20
		
		if page != 1:
			self.response.out.write("<a href=\"?p=%s\">Previous</a> | " % (page - 1))
			
		self.response.out.write(" &nbsp; %s &nbsp; " % page)
			
		self.response.out.write(" | <a href=\"?p=%s\">Next</a>" % (page + 1))
		
		self.response.out.write("<br/><br/>")
		
		self.response.out.write("<ul>")
		for tr in Transaction.gql("ORDER BY date DESC LIMIT %s, %s" % (offset, 20)):
			try:
				self.response.out.write("<li>In %s: %s <b>%s</b> %s ($%s due to \"%s\", %s)</li>" % (
											tr.group.name, 
											tr.fromMember.userNick, 
											tr.type, 
											tr.toMember.userNick, 
											tr.amount, 
											tr.reason, 
											tr.date))
			except:
				self.response.out.write("<li style=\"color:blue\">Group must have been deleted...</li>")
		self.response.out.write("</ul>")
			
def main():
    application = webapp.WSGIApplication([
                                        ('/what', WhatHandler),
                                        ], debug=True)
    
    CGIHandler().run(application)