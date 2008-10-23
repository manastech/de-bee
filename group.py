from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from model import Group
from model import Membership
from model import Transaction
from comparators import compareTransactionsByDateDesc
from comparators import compareMembershipsByUserNick
from comparators import compareMembershipsByGroupNick
from comparators import compareMembershipsByBalance
from comparators import compareMembershipsByBalanceDesc
from util import findMembershipForUser
from util import membershipsOfUser
from util import niceDate
from util import descriptionOfTransaction
from util import transactionIsBenefical
import os

class GroupHandler(webapp.RequestHandler):
    
    @login_required
    def get(self):
        # Get user, group and user membership
        user = users.get_current_user()
        group = Group.get(self.request.get("group"))   
        groupMemberships = group.memberships
        userMembership = findMembershipForUser(groupMemberships, user)
        
        # Go to homepage if someone is trying to acces this group
        # without being a member
        if not userMembership:
            self.redirect('/')
            return
        
        # Get memberships of the current user
        userMemberships = membershipsOfUser(user)
        userMemberships.sort(cmp = compareMembershipsByGroupNick)
        
        hasUserMemberships = len(userMemberships) > 0
        
        # Get user balance in this group
        [balanceSign, balance] = self.getBalance(userMembership, groupMemberships)
        
        # Get user's transaction history for the "History" tab
        try:
            transactionCount = int(self.request.get('transactionCount', default_value=10))
            transactions = self.getTransactionHistory(transactionCount, userMembership)
            transactionCount = len(transactions)
            validationError = False
            validationMessage = ''
        except BaseException, e:
            transactionCount = 0
            transactions = []
            validationError = True
            validationMessage = '(This should be a number)'
            
        # Get debtors and creditors used in the "Bal" tab
        [groupDebtors, groupCreditors, groupZero] = self.getDebtorsAndCreditors(groupMemberships)
        
        # Get members for autocomplete used in the bulk-operation box
        autocompleteMembers = self.getAutocompleteMembers(groupMemberships)
        
        # Sort the members lexicographically to display in UI
        groupMemberships.sort(cmp = compareMembershipsByUserNick)
        
        # But exclude the user from the group members
        groupMemberships = self.excludeMembership(groupMemberships, user)
        
        message = self.request.get("msg")

        template_values = {
            'username': user.nickname(),
            'signout_url': users.create_logout_url("/"),
            'goToHistoryTab': self.request.get("goToHistoryTab"),
            'balance': userMembership.balance * balanceSign,
            'balancePositive': balanceSign > 0,
            'balanceIsZero': balanceSign == 0,
            'hasMoreThanOneBalanceItem': len(balance) > 1,
            'balanceItems': balance,
            'hasGroupMemberships': len(groupMemberships) > 0,
            'groupMemberships': groupMemberships,
            'userMembership': userMembership,
            'hasTransactions': len(transactions) > 0,
            'transactionCount': transactionCount,
            'transactions': transactions,
            'validationError': validationError,
            'validationMessage': validationMessage,
            'hasUserMemberships': hasUserMemberships,
            'userMemberships': userMemberships,
            'hasMessage': not message is None and len(message) > 0,
            'message': message,
            'groupHasBalance': len(groupDebtors) > 0 or len(groupCreditors) > 0,
            'hasDebtors': len(groupDebtors) > 0,
            'groupDebtors': groupDebtors,
            'hasGroupZero': len(groupZero) > 0,
            'groupZero': groupZero,
            'hasCreditors': len(groupCreditors) > 0,
            'groupCreditors': groupCreditors,            
            'autocompleteMembers': autocompleteMembers
             }
        
        path = os.path.join(os.path.dirname(__file__), 'group.html')
        self.response.out.write(template.render(path, template_values))

    # Returns an array where the first component has the sign of the
    # balance of the given user, and the second component is an array
    # of objects whose properties are:
    #  user: the name of the user that owe/must pay
    #  amount: the amount he/she owes/must pay
    # If sign is:
    #  0: the balance of the user is zero
    #  > 0: the group members owe the user
    #  < 0: the user owe the group members 
    def getBalance(self, userMembership, groupMemberships):
        if userMembership.balance == 0.0:
            return [0, []]
        
        if userMembership.balance > 0.0:
            groupMemberships.sort(cmp = compareMembershipsByBalance)
            sign = 1
        else:
            groupMemberships.sort(cmp = compareMembershipsByBalanceDesc)
            sign = -1
            
        balance = userMembership.balance * sign
        result = []
            
        for member in groupMemberships:
            if balance <= 0.0:
                break
            
            result.append({
                           'user': member.userNick, 
                           'amount': min(balance, member.balance * -sign)
                           })
            balance -= member.balance * -sign
            
        return [sign, result]
    
    # Returns at most transactionCount transactions from the history.
    # Each returned entry is:
    #  - message: a message to display in the UI.
    #  - benefical: whether the transaction is benefical for the user or not
    def getTransactionHistory(self, transactionCount, userMembership):
        transactions_query_from = Transaction.gql("WHERE group = :1 AND fromMember = :2 ORDER BY date DESC", userMembership.group, userMembership)
        transactions_from = transactions_query_from.fetch(transactionCount)
        
        transactions_query_to = Transaction.gql("WHERE group = :1 AND toMember = :2 ORDER BY date DESC", userMembership.group, userMembership)
        transactions_to = transactions_query_to.fetch(transactionCount)
        
        transactions = transactions_from + transactions_to
        transactions.sort(cmp = compareTransactionsByDateDesc)
        
        transactions = transactions[0:transactionCount]
        
        messages = []
        for tr in transactions:
            if not tr.fromUser or not tr.toUser or not tr.creator:
                continue
            
            message = descriptionOfTransaction(tr, userMembership.user)
            message = '%s %s' % (niceDate(tr.date), message)
            messages.append({
                'message': message, 
                'benefical': transactionIsBenefical(tr, userMembership.user)
                })
             
        return messages
    
    # Returns an array of two elements, each of them being an array
    # with properties 'user' and 'amount'. The first returned element
    # is the debtors, the second is the creditors, the third are others
    def getDebtorsAndCreditors(self, groupMemberships):
        debtors = []
        creditors = []
        others = []
        
        groupMemberships.sort(cmp = compareMembershipsByBalance)
        
        for member in groupMemberships:
            tuple = {'user': member.userNick, 'amount': abs(member.balance)}
            if member.balance < 0.0:
                debtors.append(tuple)
            elif member.balance > 0.0:
                creditors.append(tuple)
            else:
                others.append(tuple)
        
        return [debtors, creditors, others]
    
    # Returns a string like 'member1', 'member2', ..., 'memberN'
    # to use in autocomplete for javascript.
    def getAutocompleteMembers(self, groupMemberships):
        autocompleteMembers = "";
        first = True
        for member in groupMemberships:
            if not first:
                autocompleteMembers += ", "
            autocompleteMembers += "'" + member.userNick + "'"            
            first = False
        return autocompleteMembers
    
    # Returns an array of memberships that are the same as groupMemberships,
    # exlcuding the one that has the given user
    def excludeMembership(self, groupMemberships, user):
        ret = []
        for member in groupMemberships:
            if member.user != user:
                ret.append(member)
        return ret