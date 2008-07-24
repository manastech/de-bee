from google.appengine.ext import webapp
from google.appengine.api import users
from model import *
import os
from google.appengine.ext.webapp import template

class GroupDetail(webapp.RequestHandler):
    def get(self):
        
        user = users.get_current_user()
        if not user:      
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        group = Group.get(self.request.get("group"))
        me = Membership.gql("WHERE group = :1 AND user = :2", group, user)[0]
        if me.balance >= 0:
            members = Membership.gql("WHERE group = :1 AND balance < 0 ORDER BY balance", group)
            sign = 1
        else:
            members = Membership.gql("WHERE group = :1 AND balance > 0 ORDER BY balance DESC", group)
            sign = -1
        
        
        balance = me.balance * sign
        result = []
        
        for member in members:
            if balance <= 0:
                break
            result.append({'user': member.user, 'amount': min(balance, member.balance * -sign)})
            balance -= member.balance * -sign
             
        
        template_values = {'balance': me.balance * sign, 'result': result }
        
        if me.balance >= 0:
            path = os.path.join(os.path.dirname(__file__), 'groupDetailPositive.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'groupDetailNegative.html')
        self.response.out.write(template.render(path, template_values))