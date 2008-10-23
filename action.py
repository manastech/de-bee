from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from ajax import userIsLoggedIn
from ajax import alertMessage
from ajax import redirectPage
from model import Membership
from model import Transaction
from email import DeBeeEmail
from email import transactionNoticeSubject
from util import UrlBuilder
from util import readFile
from util import descriptionOfTransaction

class ActionHandler(webapp.RequestHandler):
    
    def post(self):
        if not userIsLoggedIn(self):
            return
        
        user = users.get_current_user()
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
        
        # ========================================================= #
        # See what's the type of the transaction and adjust balance
        # ========================================================= #
        
        if type == 'debt':
            # If it's a debt, fromMember always looses
            fromMember.balance -= amount
            toMember.balance += amount
            
            if creatorMember.user == fromMember.user:
                # I owe someone
                mailFile = 'creator_owes_you'
            else:
                # Someone owes me
                mailFile = 'you_owe_creator'
        elif type == 'payment':
            # If it's a payment, fromMember always wins
            fromMember.balance += amount
            toMember.balance -= amount
            
            if creatorMember.user == fromMember.user:
                # I payed someone
                mailFile = 'creator_payed_you'
            else:
                # Someone payed me
                mailFile = 'you_payed_creator'
        else:
            # Can't happen, only with hackery
            return
        
        fromMember.put()
        toMember.put()
        
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
        
        # See who is me, and who is someone
        if creatorMember == fromMember:
            me = fromMember
            someone = toMember
        else:
            me = toMember
            someone = fromMember
        
        # Try send mail
        message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
        
        message.body = readFile('texts/%s.txt' % mailFile) % (someone.userNick, me.userNick, amount, reason, rejectUrl)
        message.html = readFile('texts/%s.html' % mailFile) % (someone.userNick, me.userNick, amount, reason, rejectUrl)
        
        try:
            message.send()
        except:
            iHateGoogleAppEngineMailQuotaRules = True
        
        location = '/group?group=%s&msg=%s' % (creatorMember.group.key(), descriptionOfTransaction(tr, user))
        redirectPage(self,location)