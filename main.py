#!/usr/bin/env python


import wsgiref.handlers
from google.appengine.ext import webapp
from handlers import *


def main():
  application = webapp.WSGIApplication([('/', MainHandler)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
