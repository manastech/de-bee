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
from util import descriptionOfGeneralBalance
from util import descriptionOfTotalBalance
from util import descriptionOfTotalBalanceInThisGroup
from i18n import getDefaultLanguage
from i18n import getLanguage
from i18n import addMasterKeys
from i18n import _
import os

class GroupHandler(webapp.RequestHandler):
    
    @login_required
    def get(self):
        # Get user, group and user membership
        user = users.get_current_user()
        lang = getLanguage(self, user)
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
        [balanceSign, balance] = self.getBalance(userMembership, groupMemberships, lang)
        
        # Get user's transaction history for the "History" tab
        try:
            transactionCount = int(self.request.get('transactionCount', default_value=10))
            transactions = self.getTransactionHistory(transactionCount, userMembership, lang)
            transactionCount = len(transactions)
            validationError = False
            validationMessage = ''
        except BaseException, e:
            transactionCount = 0
            transactions = []
            validationError = True
            validationMessage = '(' + _('This should be a number', lang) + ')'
            
        # Get debtors and creditors used in the "Bal" tab
        [groupDebtors, groupCreditors, groupZero] = self.getDebtorsAndCreditors(groupMemberships, lang)
        
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
            'balanceDesc': descriptionOfTotalBalanceInThisGroup(userMembership.balance, lang),
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
            'autocompleteMembers': autocompleteMembers,
            
            # i18n
            'GoToGroup': _('Go to group', lang),
            'SelectAnotherGroup': _('select another group', lang),
            'Group': _('Group', lang),
            'YourBalance': _('Your balance', lang),
            'YouOweNobody': _('You owe nobody, and nobody owes you. Hurray!', lang),
            'OweOrPay': _('Owe or Pay', lang),
            'SomeonePaysTheOthersOweHim': _('Someone pays, the others owe him/her', lang),
            'IOwed': _('I owed', lang),
            'DueTo': _('due to', lang),
            'IPaid': _('I paid', lang),
            'OwedMe': _('owed me', lang),
            'PaidMe': _('paid me', lang),
            'YouAreTheOnlyMemberInThisGroup': _('You are the only member in this group', lang),
            'GoInviteSomeone': _('Go invite someone!', lang),
            'TheresNoOneOwingNoOne': _('There\'s no one owing no one. Hooray!', lang),
            'WhatsThisFor': _('What\'s this for?', lang),
            'ViewSummary': _('View summary', lang),
            'Save': _('Save', lang),
            'EnterTheEmails': _('Enter the emails of the people you want to invite, separated by commas', lang),
            'YouCanAddAnInvitationText': _('You can add an invitation text', lang),
            'PleaseJoin': _('Please join this group and try the De-Bee experience!', lang),
            'History': _('History', lang),
            'ShowLast': _('Show last', lang),
            'Transactions': _('transactions', lang),
            'NameByWhichYouWantToSeeThisGroup': _('Name by which you want to see this group', lang),
            'NameByWhichYouWantOthersToSeeYouInThisGroup': _('Name by which you want others to see you in this group', lang),
            'CantUnsubscribe': _('At this moment you can not unsuscribe from this group, nobody must owe you and you must owe no one, your balance in the group must be zero.', lang),
            'IfYouWantToLeave': _('If you want to leave this group, click this button', lang),
            'NoTransactionsToShow': _('No transactions to show.', lang),
            'Pays': _('Pays', lang),
            'Refresh': _('Refresh', lang),
            'InviteThem': _('Invite them!', lang),
            'Unsusbribe': _('Unsusbribe', lang),
            'WhatIsBulkFor': _('WhatIsBulkFor', lang),
            'Example': _('Example', lang),
            'BulkExample': _('BulkExample', lang),
            'InThisGroup': _('in this group', lang),
            'ADinnerOut': _('A dinner out', lang),
            'WhatIsCowFor': _('WhatIsCowFor', lang),
            'CowExample': _('CowExample', lang),
            'Reason': _('Reason', lang),
        }
        
        addMasterKeys(template_values, lang)
        
        path = os.path.join(os.path.dirname(__file__), 'group.html')
        self.response.out.write(template.render(path, template_values))

    # Returns an array where the first component has the sign of the
    # balance of the given user, and the second component is a message.
    # If sign is:
    #  0: the balance of the user is zero
    #  > 0: the group members owe the user
    #  < 0: the user owe the group members 
    def getBalance(self, userMembership, groupMemberships, lang):
        if abs(userMembership.balance) <= 1e-07:
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
            if balance <= 1e-07:
                break
            
            amount = min(balance, member.balance * -sign)
            tuple = {'user': member.userNick, 'amount': round(amount, 2)}
            
            if sign == 1:
                result.append(_('%(user)s owes you $%(amount)s', lang) % tuple)
            else:
                result.append(_('You owe %(user)s $%(amount)s', lang) % tuple)
                
            balance -= member.balance * -sign
            
        return [sign, result]
    
    # Returns at most transactionCount transactions from the history.
    # Each returned entry is:
    #  - message: a message to display in the UI.
    #  - benefical: whether the transaction is benefical for the user or not
    def getTransactionHistory(self, transactionCount, userMembership, lang):
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
            
            message = descriptionOfTransaction(tr, userMembership.user, lang)
            message = '%s %s' % (niceDate(tr.date, lang), message)
            messages.append({
                'message': message, 
                'benefical': transactionIsBenefical(tr, userMembership.user)
                })
             
        return messages
    
    # Returns an array of two elements, each of them being an array
    # of messages. The first returned element
    # is the debtors, the second is the creditors, the third are others
    def getDebtorsAndCreditors(self, groupMemberships, lang):
        debtors = []
        creditors = []
        others = []
        
        groupMemberships.sort(cmp = compareMembershipsByBalance)
        
        for member in groupMemberships:
            desc = descriptionOfGeneralBalance(member, lang)
            if member.balance < 0.0:
                debtors.append(desc)
            elif member.balance > 0.0:
                creditors.append(desc)
            else:
                others.append(desc)
        
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