from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from ajax import redirectPage
from ajax import userIsLoggedIn
from model import Transaction
from emails import someoneOwedYou
from emails import youOwedSomeone
from emails import someonePayedYou
from emails import youPayedSomeone
from emails import createRejectionMail
from emails import sendEmail
from util import descriptionOfTransaction
from util import transactionIsBenefical
from i18n import getLanguage
import os

class RejectHandler(webapp.RequestHandler):
    
    @login_required
    def get(self):
        key = self.request.get('key')
        hash = self.request.get('h')
        user = users.get_current_user()
        lang = getLanguage(self, user)
        
        # Check that all is ok
        tr = isValidTransaction(key, hash, user)
        if not tr:
            self.redirect('/')
            return
        
        template_values = {
                'key' : key,
                'h' : hash,
                'group' : tr.group,
                'username' : user.nickname(),
                'transactionDescription': descriptionOfTransaction(tr, user, lang),
                'transactionIsBenefical': transactionIsBenefical(tr, user),
                'alreadyRejected': tr.isRejected,
            }
                   
        path = os.path.join(os.path.dirname(__file__), 'reject.html')
        self.response.out.write(template.render(path, template_values))
        return
        
class CommitRejectHandler(webapp.RequestHandler):
    
    def post(self):
        if not userIsLoggedIn(self):
            return
        
        key = self.request.get('key')
        hash = self.request.get('h')
        reason = self.request.get('reason').strip()
        user = users.get_current_user()
        
        # Check that all is ok
        tr = isValidTransaction(key, hash, user)
        if not tr:
            self.redirect('/')
            return
        
        # Check that the transaction is not rejected
        if tr.isRejected:
            self.redirect('/')
            return
        
        # Reject it and everything else...
        tr.isRejected = True
        
        compensateTr = tr.getCompensateFor(user)
        
        # See who is me, and who is someone
        if compensateTr.creatorMember == compensateTr.fromMember:
            me = compensateTr.fromMember
            someone = compensateTr.toMember
        else:
            me = compensateTr.toMember
            someone = compensateTr.fromMember
            
        someoneLang = getLanguage(self, someone.user)
            
        balanceBefore = someone.balance

        # ========================================================= #
        # See what's the type of the transaction and adjust balance
        # ========================================================= #
        
        if tr.type == 'debt':
            # If it's a debt, fromMember always wins
            tr.fromMember.balance += tr.amount
            tr.toMember.balance -= tr.amount
            
            if compensateTr.creatorMember.user == tr.fromMember.user:
                # I owe someone
                mailBody = someoneOwedYou(someoneLang, reject = True)
            else:
                # Someone owes me
                mailBody = youOwedSomeone(someoneLang, reject = True)
        elif tr.type == 'payment':
            # If it's a payment, fromMember always looses
            tr.fromMember.balance -= tr.amount
            tr.toMember.balance += tr.amount
            
            if compensateTr.creatorMember.user == tr.fromMember.user:
                # I paid someone
                mailBody = someonePayedYou(someoneLang, reject = True)
            else:
                # Someone paid me
                mailBody = youPayedSomeone(someoneLang, reject = True)
        else:
            # Can't happen, only with hackery
            return
        
        tr.fromMember.put()
        tr.toMember.put()
        tr.put()
        compensateTr.put()
        
        balanceNow = someone.balance

        # ========================== #
        # Try send notification mail #
        # ========================== #        
        
        # Try send mail
        message = createRejectionMail(me, someone, tr, reason, balanceBefore, balanceNow, mailBody, someoneLang)
        sendEmail(message)
        
        location = '/group?group=%s&msg=%s' % (tr.group.key(), 'You rejected the transaction')
        redirectPage(self,location)
        
def isValidTransaction(key, hash, user):
    # Check that the parameters exist
        if not key or not hash:
            return False
        
        # Check that the transaction exists
        tr = Transaction.get(key)
        if not tr:
            return False
        
        # Check that the current user is involved in the transaction
        if user != tr.fromUser and user != tr.toUser:
            return False
        
        # Check that the hash if valid
        if not tr.isValidHash(hash):
            return
        
        return tr