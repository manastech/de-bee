from google.appengine.ext import webapp
from wsgiref.handlers import CGIHandler
from model import Membership
from model import Group
from model import Transaction
import math

class TransactionsHandler(webapp.RequestHandler):
    
    def get(self):
        groupKey = self.request.get('key')
        group = Group.get(groupKey)
        
        self.response.out.write("<h1>Transactions in %s</h1>" % group.name)
        
        balances = {}
        
        transactions = Transaction.gql("WHERE group = :1 ORDER BY date ASC", group)
        
        self.response.out.write("<ul>")
        for tr in transactions:
            try:
                self.response.out.write("<li>");
                self.response.out.write("Creator: %s, From: <b>%s</b>, To: <b>%s</b>, Type: <b>%s</b>, Amount: %s, Reason: %s, Date: %s"
                                        % (tr.creatorMember.user.nickname(), 
                                           tr.fromMember.user.nickname(), 
                                           tr.toMember.user.nickname(),
                                           tr.type, 
                                           tr.amount, 
                                           tr.reason, 
                                           tr.date))
                
                if tr.type == "debt":
                    fromBalance = -tr.amount
                    toBalance = tr.amount
                else:
                    fromBalance = tr.amount
                    toBalance = -tr.amount
                    
                if not tr.fromMember.user in balances:
                    balances[tr.fromMember.user] = fromBalance
                else:
                    balances[tr.fromMember.user] += fromBalance
                    
                if not tr.toMember.user in balances:
                    balances[tr.toMember.user] = toBalance
                else:
                    balances[tr.toMember.user] += toBalance
                    
                totalBalance = 0.0
                    
                self.response.out.write("<ul>");
                for member, balance in balances.items():
                    totalBalance += balance
                    self.response.out.write("<li>%s: %s</li>" % (member, balance));
                if abs(totalBalance - 0) > 1e7:
                    self.response.out.write("<li style=\"color:red\">Total Balance: %s</li>" % totalBalance);
                self.response.out.write("</ul>");
                    
                self.response.out.write("</li>");
            except:
                foo = True
        self.response.out.write("</ul>")
            
def main():
    application = webapp.WSGIApplication([
                                        ('/transactions', TransactionsHandler),
                                        ], debug=True)
    
    CGIHandler().run(application)