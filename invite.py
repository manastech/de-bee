from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from ajax import userIsLoggedIn
from ajax import redirectPage
from ajax import alertMessage
from model import Group
from model import Membership
from util import UrlBuilder
from io import readFile
from emails import DeBeeEmail
from cgi import escape
from hashlib import sha224
from i18n import getLanguage
from i18n import addMasterKeys
from i18n import _
import os

class GroupInvitation:
    
    def __init__(self, toGroup, toEmail, urlBuilder):
        self.toGroup = toGroup
        self.toEmail = toEmail
        self.urlBuilder = urlBuilder
        
    def getUrl(self):
        return self.urlBuilder.buildUrl("/acceptInvitation?group=%s&user=%s&hash=%s" % (str(self.toGroup.key()) , self.toEmail , self.makeHash()))
    
    def makeHash(self):
        m = sha224()
        m.update(str(self.toGroup.key()))
        m.update(self.toEmail)
        return m.hexdigest()

class InviteHandler(webapp.RequestHandler):

    def post(self):
        if not userIsLoggedIn(self):
            return
        
        user = users.get_current_user()
        lang = getLanguage(self, user)
        groupKey = self.request.get('group')
        group = Group.get(groupKey)
        invitationText = self.request.get('invitationText')
        emails = self.request.get('emails')
        emails = emails.split(',')
        urlBuilder = UrlBuilder(self.request)
        
        # Check that all emails are valid
        for email in emails:
        	if not mail.is_email_valid(email.strip()):
        		alertMessage(self, _('%s is not a valid email address', lang) % email)
        		return
        
        for email in emails:
            self.sendInvitation(user, email.strip(), group, invitationText, urlBuilder, lang)
            
        redirectPage(self, "/group?group=%s&msg=%s" % (groupKey, escape(_('Your invite has been sent!', lang))))
        
    def sendInvitation(self, fromUser, toEmail, toGroup, customInvitationText, urlBuilder, lang):
        invitation = GroupInvitation(toGroup, toEmail, urlBuilder)
        plainUrl = invitation.getUrl()
        subject = "De-Bee: You are invited to %s group!" % toGroup.name
        
        message = mail.EmailMessage(
                        sender = DeBeeEmail, 
                        to = toEmail, 
                        subject = subject)
        
        if len(customInvitationText) > 0:
            plainInvitationText = customInvitationText + '\n\n'
            htmlInvitationText = customInvitationText + '<br><br>'
        else:
            plainInvitationText = ''
            htmlInvitationText = ''
        
        invitationText = readFile('texts/%s/invitation.txt' % lang)
        invitationHtml = readFile('texts/%s/invitation.html' % lang)
        
        membersText = ''
        membersHtml = '<ul>'
        
        for member in toGroup.memberships:
            if member.userNick != member.user.email():
                membersText += ' * %s (%s)\n' % (member.userNick, member.user.email())
                membersHtml += '<li>%s (%s)</li>' % (member.userNick, member.user.email())
            else:
                membersText += ' * %s\n' % member.userNick
                membersHtml += '<li>%s</li>' % member.userNick
                
        membersHtml += '</ul>'
        
        message.body = invitationText % (toEmail, fromUser, toGroup.name, plainInvitationText, membersText, plainUrl)
        message.html = invitationHtml % (toEmail, fromUser, toGroup.name, htmlInvitationText, membersHtml, plainUrl)
        
        try:
            message.send()
        except:
            iHateGoogleAppEngineMailQuotaRules = True
            
class AcceptInvitationHandler(webapp.RequestHandler):
    
    @login_required
    def get(self):
        user = users.get_current_user()
        lang = getLanguage(self, user)
        groupKey = self.request.get("group")
        try:
            group = Group.get(groupKey)
            email = self.request.get("user")
            invitation = GroupInvitation(group, email, UrlBuilder(self.request))
        
            # Verificar que la invitacion es valida (coinciden los hashes)
            isValidInvitation = invitation.makeHash() == self.request.get("hash")
            
            # Verificar que el usuario logueado coincide con el mail de la invitacion
            isValidUser = user.email().lower() == email.lower()
        except:
            group = None
            isValidInvitation = False
            isValidUser = False
        
        if not isValidInvitation or not isValidUser:
            template_values = {
                'isValidInvitation': isValidInvitation,
                'isValidUser': isValidUser,
                'group': group,
                'username': user.nickname(),
                'signout_url': users.create_logout_url("/"),
                
                # i18n
                'ThisInvitationIsNotForYou': _('This invitation is not for you.', lang),
                'TheInvitationIsInvalid': _('The invitation is invalid.', lang)
            }
            
            addMasterKeys(template_values, lang)
            
            path = os.path.join(os.path.dirname(__file__), 'acceptInvitationError.html')
            self.response.out.write(template.render(path, template_values))
            return
        
        # Verificar que el usuario no sea miembro del grupo
        isMember = Membership.gql("WHERE user = :1 AND group = :2", user, group).count() > 0
           
        # If he's already a member, don't bother showing her that.
        # Just redirect to the group page with an appropriate message.
        if not isMember:
            
            msg = _('You are now a member of %s group', lang) % group.name
             
            # Join the user into the group. If later she finds out she has two
            # groups with the same name, she'll already know she can change the name
            # because she already belonged to another group... so she must know the site
            
            Membership(
                    user = user,
                    group = group,
                    balance = 0.0,
                    alias = group.name
                ).put()
                
        else:
            msg = _('You are already a member of this group', lang)
        
        self.redirect('/group?group=%s&msg=%s' % (group.key(), msg))