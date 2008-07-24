#!/usr/bin/env python


from google.appengine.ext import webapp
from handlers import *
from enterTransactionHandler import *
from registerTransactionHandler import *
from mail_handler import *
from groupHandlers import *
from model import *
from groupDetail import *
import wsgiref.handlers

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                    ('/mail', MailHandler),
									('/registerTransaction', RegisterTransactionHandler),
                                    ('/enterTransaction', EnterTransactionHandler),
                                    ('/transactionHistory', TransactionHistory),
                                    ('/groupDetail', GroupDetail),
					('/groupCreation', GroupCreationHandler),
					('/enterGroupCreation', EnterGroupCreationHandler),
					('/groupInvitation', GroupInvitationHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
