from google.appengine.ext import webapp
from google.appengine.api import users
from model import Membership
from model import Group
from ajax import alertMessage
from ajax import redirectPage
from ajax import userIsLoggedIn
from cgi import escape

class CreateGroupHandler(webapp.RequestHandler):
    
    def post(self):
        if not userIsLoggedIn(self):
            return
        
        groupName = self.request.get('name').strip()
        escapedGroupName = escape(groupName)

        # Verificar que el nombre no sea vacio
        if groupName == "": 
            error = 'You must enter a group name.'
            alertMessage(self,error)
            return
        
        group = self.createGroupAndInsertMember(groupName)

        # Si el usuario es miembro de un grupo con alias igual al nombre 
        # del grupo que quiere crear, no dejarlo
        if group is None: 
            error = 'You already belong to a group with the name ' + escapedGroupName + '.\nPlease select another name.'
            alertMessage(self,error)
            return

        location = '/group?group=%s&msg=%s' % (group.key(), 'Group successfully created')
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