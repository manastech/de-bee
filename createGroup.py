from google.appengine.ext import webapp
from google.appengine.api import users
from model import Membership
from model import Group
from ajax import alertMessage
from ajax import redirectPage
from ajax import userIsLoggedIn
from i18n import getLanguage
from i18n import _
from cgi import escape

class CreateGroupHandler(webapp.RequestHandler):
    
    def post(self):
        if not userIsLoggedIn(self):
            return
        
        user = users.get_current_user()
        lang = getLanguage(self.request, user)
        
        groupName = self.request.get('name').strip()
        escapedGroupName = escape(groupName)

        # Verificar que el nombre no sea vacio
        if groupName == "": 
            error = _('You must enter a group name.', lang)
            alertMessage(self,error)
            return
        
        group = self.createGroupAndInsertMember(groupName)

        # Si el usuario es miembro de un grupo con alias igual al nombre 
        # del grupo que quiere crear, no dejarlo
        if group is None: 
            error = _('You already belong to a group with the name %s.', lang) % escapedGroupName
            error += '\\n';
            error += _('Please select another name.', lang)
            alertMessage(self,error)
            return

        location = '/group?group=%s&msg=%s' % (group.key(), _('Group successfully created', lang))
        redirectPage(self,location)

    def insertUserInGroup(self, group):
        membership = Membership(
                        user = users.get_current_user(),
                        group = group,
                        balance = 0.0,
                        alias = group.name)
        membership.put()

    def createGroupAndInsertMember(self, gname):
        user = users.get_current_user()
        count = Membership.gql("WHERE user = :1 AND alias = :2", user, gname).count()
        if count > 0:
            return None
        group = Group(name=gname)
        group.put()
        
        self.insertUserInGroup(group)
        return group