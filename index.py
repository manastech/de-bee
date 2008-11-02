from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from model import Membership
from util import membershipsOfUser
from util import descriptionOfBalanceInGroup
from util import descriptionOfTotalBalance
from comparators import compareMembershipsByGroupNick
from i18n import getDefaultLanguage
from i18n import getLanguage
from i18n import addMasterKeys
from i18n import _
import os

class IndexHandler(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()

    if user:
        lang = getLanguage(self, user)
        
        userMemberships = membershipsOfUser(user)
        userMemberships.sort(cmp = compareMembershipsByGroupNick)
        
        hasUserMemberships = len(userMemberships) > 0
        
        if hasUserMemberships:
            group = userMemberships[0].group
        else:
            group = 0
            
        debts = self.getDebts(user, userMemberships, lang)
        
        message = self.request.get('msg')
        hasMessage = len(message) > 0
        
        model = { 
            'username': user.nickname(),
            'signout_url': users.create_logout_url("/"),
            'debts': debts,
            'hasUserMemberships': hasUserMemberships,
            'userMemberships': userMemberships,
            'group': group,
            'hasMessage': hasMessage,
            'message': message,
            
            # i18n
            'DontBelong': _("You don't belong to any group. You can create your own and invite your friends.", lang),
            'Name': _('Name', lang),
            'YouOweNobody': _('You owe nobody, and nobody owes you. Hurray!', lang),
            'GoToGroup': _('Go to group', lang),
            'SelectGroup': _('select group', lang),
        }
        
        addMasterKeys(model, lang)
        
        path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
        self.response.out.write(template.render(path, model))
            
    else:
        lang = getDefaultLanguage(self)
        
        model = {
                 'loginurl': users.create_login_url("/"),
                 
                 # i18n
                 'introduction': _('introduction', lang),
            }
        
        addMasterKeys(model, lang)
        
        path = os.path.join(os.path.dirname(__file__), 'introduction.html')
        self.response.out.write(template.render(path, model))
    
  def getDebts(self, user, memberships, lang):    
    total = 0
    items = []
    for m in memberships:
        if m.balance == 0.0:
            continue
        
        link = '/group?group=%s' % m.group.key()
        total += m.balance
        items.append({
            'isOweToSelf' : m.balance > 0.0, 
            'desc': descriptionOfBalanceInGroup(m, link, lang)
            })
    
    return {
            'isZero': total == 0.0, 
            'isOweToSelf' : total > 0.0, 
            'items' : items,
            'desc': descriptionOfTotalBalance(total, lang),
            'hasMoreThanOneItem' : len(items) > 1,
            }