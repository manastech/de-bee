#!/usr/bin/env python

from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler
from index import IndexHandler
from group import GroupHandler
from createGroup import CreateGroupHandler
from changeGroupProperties import ChangeGroupPropertiesHandler
from invite import InviteHandler
from invite import AcceptInvitationHandler
from action import ActionHandler
from bulk import BulkHandler
from reject import RejectHandler
from reject import CommitRejectHandler
from unsubscribe import UnsubscribeHandler

def main():
  application = webapp.WSGIApplication([
					('/', IndexHandler),
                    ('/group',GroupHandler),
                    ('/createGroup', CreateGroupHandler),
                    ('/changeGroupProperties', ChangeGroupPropertiesHandler),
                    ('/invite', InviteHandler),
                    ('/acceptInvitation', AcceptInvitationHandler),
                    ('/action', ActionHandler),
                    ('/bulk', BulkHandler),
                    ('/unsubscribe', UnsubscribeHandler),
                    ('/reject', RejectHandler),
                    ('/commitReject', CommitRejectHandler),
                    ],
                    debug=True)
  CGIHandler().run(application)

if __name__ == '__main__':
  main()
