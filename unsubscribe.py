from google.appengine.api import users
from google.appengine.ext import webapp
from model import Membership
from model import Group
from ajax import alertMessage
from ajax import redirectPage
from ajax import userIsLoggedIn
from i18n import getLanguage
from i18n import _
from cgi import escape

class UnsubscribeHandler(webapp.RequestHandler):

    def post(self):
        if not userIsLoggedIn(self):
            return
        
        user = users.get_current_user()
        lang = getLanguage(self, user)
        
        groupKey = self.request.get('group').strip()
        
        if groupKey == "":
            error = _('Group is required', lang)
            alertMessage(self,error)
            return
        
        group = Group.get(groupKey)
        memberships = Membership.gql("WHERE group = :1 AND user = :2", group, user)

        if memberships.count() <> 1:
            error = _('You don\'t belong to this group.', lang)
            alertMessage(self,error)
            return
        
        membership = memberships.get()
        if not abs(membership.balance) <= 1e-07:
            error = _('You cannot leave this group, your balance must be zero.', lang)
            alertMessage(self,error)
            return
        
        membership.delete()
        if Membership.gql("WHERE group = :1", group).count() == 0:
            group.delete()
        
        msg = _('You have been succesfully unsubscribed from the group %s!', lang) % escape(group.name)
        location = '/?msg=' + msg
        redirectPage(self,location)