#!/usr/bin/env python

from google.appengine.ext import webapp
from handlers import *
from registerTransactionHandler import *
from registerInviteHandler import *
from groupInvitationHandler import *
from mail_handler import *
from groupHandlers import *
from bulk import *
from model import *
from userGroupUnsubscription import *
import wsgiref.handlers

class WhoHandler(webapp.RequestHandler):
	
	def get(self):
		for me in Membership.all():
			self.response.out.write('In group <b>%s</b>, <b>%s</b> has a balance of <b>%s</b><br/>' % (me.group.name, me.user.email(), me.balance)) 

def main():
  application = webapp.WSGIApplication([
					('/', MainHandler),
					('/registerTransaction', RegisterTransactionHandler),
                    ('/registerInvite', RegisterInviteHandler),
                    ('/groupCreation', GroupCreationHandler),
                    ('/group',GroupHandler),
                    ('/reject', RejectTransactionHandler),
                    ('/doReject', DoRejectTransactionHandler),
                    ('/enterUnsubscription', EnterUnsubscriptionHandler),
                    ('/groupUnsubscription', UnsubscriptionHandler),
					('/groupInvitation', GroupInvitationHandler),
                    ('/groupJoin', GroupJoinHandler),
                    ('/groupChangeAlias', GroupChangeAliasHandler),
                    ('/bulkDo', BulkDoHandler),
                    ('/bulkSummary', BulkSummaryHandler),
                    ('/who', WhoHandler),
                    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
