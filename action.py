from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from ajax import userIsLoggedIn
from ajax import alertMessage
from ajax import redirectPage
from model import Membership
from model import Transaction
from emails import someoneOwedYou
from emails import youOwedSomeone
from emails import someonePayedYou
from emails import youPayedSomeone
from emails import createActionMail
from emails import sendEmail
from util import UrlBuilder
from util import descriptionOfTransaction
from i18n import getLanguage

class ActionHandler(webapp.RequestHandler):
    
    def post(self):
        if not userIsLoggedIn(self):
            return
        
        user = users.get_current_user()
        lang = getLanguage(self, user)
        type = self.request.get('type')
        fromMember = Membership.get(self.request.get('fromMember'))
        toMember = Membership.get(self.request.get('toMember'))
        amount = self.request.get('amount')
        reason = self.request.get('reason')
        
        # See which one is the creator
        if fromMember.user == user:
            creatorMember = fromMember 
        elif toMember.user == user:
            creatorMember = toMember
        else:
            # Can't happen, only with hackery
            return
        
        # Check that the amount is a valid number
        try:
          amount = float(amount)
        except BaseException, e:
            error = 'Invalid amount: %s.' % amount
            alertMessage(self, error)
            return
        
        # Check that it is positive
        if amount <= 0:
            error = 'Invalid amount: %s.' % amount
            alertMessage(self, error)
            return
        
        # See who is me, and who is someone
        if creatorMember == fromMember:
            me = fromMember
            someone = toMember
        else:
            me = toMember
            someone = fromMember
            
        someoneLang = getLanguage(self, someone.user)
        
        balanceBefore = someone.balance
        
        # ========================================================= #
        # See what's the type of the transaction and adjust balance
        # ========================================================= #
        
        if type == 'debt':
            # If it's a debt, fromMember always looses
            fromMember.balance -= amount
            toMember.balance += amount
            
            if creatorMember.user == fromMember.user:
                # I owe someone
                mailBody = someoneOwedYou(someoneLang)
            else:
                # Someone owes me
                mailBody = youOwedSomeone(someoneLang)
        elif type == 'payment':
            # If it's a payment, fromMember always wins
            fromMember.balance += amount
            toMember.balance -= amount
            
            if creatorMember.user == fromMember.user:
                # I paid someone
                mailBody = someonePayedYou(someoneLang)
            else:
                # Someone paid me
                mailBody = youPayedSomeone(someoneLang)
        else:
            # Can't happen, only with hackery
            return
        
        fromMember.put()
        toMember.put()
        
        balanceNow = someone.balance
        
        # ============================================= #
        # Create the transaction and save it in history
        # ============================================= #
        
        tr = Transaction(
            group = creatorMember.group,
            creatorMember = creatorMember, 
            fromMember = fromMember, 
            toMember = toMember,
            type = type,
            amount = amount, 
            reason = reason,
            isRejected = False
            )
        tr.put()
            
        # ========================== #
        # Try send notification mail #
        # ========================== #
        
        # Build the reject url
        rejectUrl = UrlBuilder(self.request).buildUrl('/reject')
        rejectUrl += "?key=%s&h=%s" % (str(tr.key()), tr.hash)
        
        # Try send mail
        message = createActionMail(me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody, someoneLang)
        sendEmail(message)
        
        location = '/group?group=%s&msg=%s' % (creatorMember.group.key(), descriptionOfTransaction(tr, user, lang))
        redirectPage(self,location)