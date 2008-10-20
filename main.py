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
                    ],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
