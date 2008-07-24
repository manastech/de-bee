#!/usr/bin/env python


from google.appengine.ext import webapp
from handlers import *
from enterTransactionHandler import *
from registerTransactionHandler import *
from model import *
import wsgiref.handlers

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
									('/mail', MailHandler),
									('/registerTransaction', RegisterTransactionHandler),
                                    ('/enterTransaction', EnterTransactionHandler),
                                    ('/transactionHistory', TransactionHistory),
					('/groupCreation', GroupCreationHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
