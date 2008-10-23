from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from model import Membership
from util import membershipsOfUser
from comparators import compareMembershipsByGroupNick
import os

class IndexHandler(webapp.RequestHandler):

  def get(self):
    user = users.get_current_user()

    if user:
        userMemberships = membershipsOfUser(user)
        userMemberships.sort(cmp = compareMembershipsByGroupNick)
        
        hasUserMemberships = len(userMemberships) > 0
        
        if hasUserMemberships:
            group = userMemberships[0].group
        else:
            group = 0
            
        debts = self.getDebts(user, userMemberships)
        
        message = self.request.get('msg')
        hasMessage = len(message) > 0
        
        model = { 
            'username' : user.nickname(),
            'signout_url' : users.create_logout_url("/"),
            'debts' : debts,
            'hasUserMemberships' : hasUserMemberships,
            'userMemberships' : userMemberships,
            'group' : group,
            'hasMessage' : hasMessage,
            'message' : message,
            }
        
        path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
        self.response.out.write(template.render(path, model))
            
    else:
        model = {'loginurl': users.create_login_url("/")}
        path = os.path.join(os.path.dirname(__file__), 'introduction.html')
        self.response.out.write(template.render(path, model))
    
  def getDebts(self, user, memberships):    
    total = 0
    items = []
    for m in memberships:
        if m.balance == 0.0:
            continue
        
        total += m.balance
        items.append({
            'isZero': m.balance == 0.0, 
            'isOweToSelf' : m.balance > 0.0, 
            'amount' : abs(m.balance), 
            'group' : m.group, 
            'name' : m.groupNick, 
            })
    return {
            'isZero': total == 0.0, 
            'isOweToSelf' : total > 0.0, 
            'total' : abs(total), 
            'items' : items, 
            'hasMoreThanOneItem' : len(items) > 1,
            }