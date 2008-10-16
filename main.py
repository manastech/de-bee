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

def main():
#  group = Group.get('agZkZS1iZWVyCwsSBUdyb3VwGB0M')
#  user = users.get_current_user();
#  if user:
#  	Membership(user=user,group=group,balance=0.0,alias='Work').put()
	
  application = webapp.WSGIApplication([
					('/', MainHandler),
					('/registerTransaction', RegisterTransactionHandler),
                    ('/registerInvite', RegisterInviteHandler),
                    ('/groupCreation', GroupCreationHandler),
                    ('/group',GroupHandler),
                    ('/reject', RejectTransactionHandler),
                    ('/enterUnsubscription', EnterUnsubscriptionHandler),
                    ('/groupUnsubscription', UnsubscriptionHandler),
					('/groupInvitation', GroupInvitationHandler),
                    ('/groupJoin', GroupJoinHandler),
                    ('/groupChangeAlias', GroupChangeAliasHandler),
                    ('/bulkDo', BulkDoHandler),
                    ('/bulkSummary', BulkSummaryHandler),
                    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
