from google.appengine.api import users
from google.appengine.ext import webapp
from model import Membership
from model import Group
from ajax import alertMessage
from ajax import redirectPage
from ajax import userIsLoggedIn
from cgi import escape

class UnsubscribeHandler(webapp.RequestHandler):

    def post(self):
        if not userIsLoggedIn(self):
            return
        
        user = users.get_current_user()
        
        groupKey = self.request.get('group').strip()
        
        if groupKey == "":
            error = 'Group is required'
            alertMessage(self,error)
            return
        else:
            group = Group.get(groupKey)
            memberships = Membership.gql("WHERE group = :1 AND user = :2", group, user)

            if memberships.count() <> 1:
                error = 'You are not registered in this group.'
                alertMessage(self,error)
                return
            else:
                membership = memberships.get()
                if not membership.balance == 0.0:
                    error = 'You cannot leave this group, your balance must be zero.'
                    alertMessage(self,error)
                    return
                else:
                    membership.delete()
                    if Membership.gql("WHERE group = :1", group).count() == 0:
                        group.delete()
                    
                    msg = 'You have been succesfully unsubscribed from the group ' + escape(group.name) + '!'
                    location = '/?msg=' + msg
                    redirectPage(self,location)