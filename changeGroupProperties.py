from google.appengine.api import users
from google.appengine.ext import webapp
from ajax import userIsLoggedIn
from ajax import alertMessage
from ajax import redirectPage
from model import Membership
from i18n import getLanguage
from i18n import _

class ChangeGroupPropertiesHandler(webapp.RequestHandler):
    
    def post(self):
		if not userIsLoggedIn(self):
			return
            
		user = users.get_current_user()
		lang = getLanguage(self, user)
		userMembership = Membership.get(self.request.get('userMembership'))
        
		# Verificar que la membership que se paso sea efectivamente del usuario
		if not self.isMember(userMembership):
		    return
		
		newGroupNick = self.request.get('groupNick').strip()
		newUserNick = self.request.get('userNick').strip()
		
		# Verificar que el nombre de grupo no sea vacio
		if newGroupNick == "":
		    error = _('The name by which you want to see this group is required.', lang)
		    alertMessage(self,error)
		    return
		
		# Verificar que no exista un alias del usuario con el mismo nombre
		if self.isGroupNickTaken(newGroupNick, userMembership.group):
		    error = _('You already have a Group with the selected name, please select another name.', lang)
		    alertMessage(self,error)
		    return
		
		# Verificar que el nickname no sea vacio
		if newUserNick == "":
		    error = _('The name by which you want others to see you in this group is required.', lang)
		    alertMessage(self,error)
		    return
		
		# Verificar que el nickname no este tomado
		for other in Membership.gql("WHERE group = :1 AND user != :2", userMembership.group, userMembership.user):
		    if other.userNick == newUserNick:
		        error = _('The name by which you want others to see you in this group is already used by another member.', lang)
		        alertMessage(self,error)
		        return
		
		userMembership.alias = newGroupNick
		userMembership.nickname = newUserNick
		userMembership.put()
		
		location = '/group?group=%s&msg=%s' % (userMembership.group.key(), _('Properties changed!', lang))
		redirectPage(self,location)
            
    def isMember(self, membership):
        user = users.get_current_user()
        return membership.user == user 
    
    def isGroupNickTaken(self, alias, group):
        user = users.get_current_user()
        return Membership.gql("WHERE user = :1 AND alias = :2 AND group != :3", user, alias, group).count() > 0