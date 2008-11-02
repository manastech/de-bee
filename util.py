from model import Membership
from datetime import datetime
from re import compile
from i18n import _

class UrlBuilder:
    def __init__(self, webrequest):
        p = compile("[^:]*://[^/]*")
        m = p.match(webrequest.url)
        self.baseUrl = m.group()

    # without trailing /
    def getBaseUrl(self):
        return self.baseUrl
    
    def buildUrl(self, url):
        if url[0] != '/':
            url = "/%s" % url
        return "%s%s" % (self.getBaseUrl(), url)

# Returns all memberships of the given user, in no
# particular order
def membershipsOfUser(user):
    memberships = Membership.gql("WHERE user = :1", user)
    return memberships.fetch(10000)

# Returns a date formatted nicely, comparing it to the current date.
def niceDate(t):
    now = datetime.now()
    if now.year == t.year:
        if now.month == t.month and now.day == t.day:
            return t.strftime("Today at %H:%S")
        return t.strftime("On %b %d")
    else:
        return t.strftime("On %D")
    
# Returns a membership amongst the given ones, where the user
# is the given one. Return None if no one is found.
def findMembershipForUser(memberships, user):
    for membership in memberships:
        if membership.user == user:
            return membership
    return None

# Returns the description of a transaction according to
# a users's point of view. This does not include the date
# of the transaction.
def descriptionOfTransaction(tr, user):
    message = ''
    if (tr.type == "debt"):
         if (tr.fromUser == user):
             message = "You owed %(user)s $%(amount)s" % {'user': tr.toMember.userNick, 'amount': tr.amount}
         else:
             message = "%(user)s owed you $%(amount)s" % {'user': tr.fromMember.userNick, 'amount': tr.amount}
    if (tr.type == "payment"):
         if (tr.fromUser == user):
             message = "You paid %(user)s $%(amount)s" % {'user': tr.toMember.userNick, 'amount': tr.amount}
         else:
             message = "%(user)s paid you $%(amount)s" % {'user': tr.fromMember.userNick, 'amount': tr.amount}
    if (tr.type == "rejectedDebt"):
        if (tr.creator == user):
            if tr.fromUser == user:
                message = "You rejected that you owed %(user)s $%(amount)s" % {'user': tr.toMember.userNick, 'amount': tr.amount}
            else:
                message = "You rejected that %(user)s owed you $%(amount)s" % {'user': tr.toMember.userNick, 'amount': tr.amount}
        else:
            if tr.fromUser == user:
                message = "%(user)s rejected that you owed him/her $%(amount)s" % {'user': tr.fromMember.userNick, 'amount': tr.amount}
            else:
                message = "%(user)s rejected that he/she owed you $%(amount)s" % {'user': tr.fromMember.userNick, 'amount': tr.amount}
    if (tr.type == "rejectedPayment"):
        if (tr.creator == user):
            if tr.fromUser == user:
                message = "You rejected that you paid %(user)s $%(amount)s" % {'user': tr.toMember.userNick, 'amount': tr.amount}
            else:
                message = "You rejected from %(user)s a payment of $%(amount)s" % {'user': tr.toMember.userNick, 'amount': tr.amount}
        else:
            if tr.fromUser == user:
                message = "%(user)s rejected that you paid him/her $%(amount)s" % {'user': tr.fromMember.userNick, 'amount': tr.amount}
            else:
                message = "%(user)s rejected that he/she paid you $%(amount)s" % {'user': tr.fromMember.userNick, 'amount': tr.amount}
    if len(tr.reason) > 0:
         message += " due to %s" % tr.reason
    return message

# Determines if a transaction is benefical for a user
# involved in a transaction
def transactionIsBenefical(tr, user):
    if (tr.type == "debt"):
         return tr.toUser == user
    if (tr.type == "payment"):
         return tr.fromUser == user
    if (tr.type == "rejectedDebt"):
        return tr.fromUser == user
    if (tr.type == "rejectedPayment"):
        return tr.toUser == user
    
def descriptionOfBalance(balance, before):
    if before:
        if balance == 0.0:
            return 'you owed no one, and no one owed you'
        elif balance > 0.0:
            return 'they owed you $%s' % abs(balance)
        else:
            return 'you owed $%s' % abs(balance)
    else:
        if balance == 0.0:
            return 'you owe no one, and no one owes you'
        elif balance > 0.0:
            return 'they owe you $%s' % abs(balance)
        else:
            return 'you owe $%s' % abs(balance)

def descriptionOfTotalBalance(balance, lang):
    if balance == 0.0:
        return _('You owe nobody, and nobody owes you. Hurray!', lang)
    elif balance < 0.0:
        return _('You owe a total of $%s', lang) % -balance
    else:
        return _('They owe you a total of $%s', lang) % balance

def descriptionOfBalanceInGroup(membership, link, lang):
    if membership.balance < 0.0:
        return _('You owe $%(amount)s in <a href="%(link)s">%(group)s</a>', lang) % {'amount': -membership.balance, 'group': membership.groupNick, 'link': link}
    elif membership.balance > 0.0:
        return _('They owe you $%(amount)s in <a href="%(link)s">%(group)s</a>', lang) % {'amount': membership.balance, 'group': membership.groupNick, 'link': link}
    else:
        raise "Don't invoke this method with m.balance == 0.0"