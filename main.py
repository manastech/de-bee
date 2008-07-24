#!/usr/bin/env python


import wsgiref.handlers
from google.appengine.ext import webapp
from handlers import *
from model import *

def main():
  application = webapp.WSGIApplication([('/', MainHandler), 
									('/registerTransaction', RegisterTransactionHandler),
                                    ('/enterTransaction', EnterTransactionHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
