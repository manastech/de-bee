from model import Membership
from datetime import datetime
from re import compile
from i18n import _
import locale

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
def niceDate(t, lang):
	try:
		locale.setlocale(locale.LC_ALL, lang)
	except:
		localeNotSupported = True
	
	now = datetime.now()
	if now.year == t.year:
	    if now.month == t.month and now.day == t.day:
	        return t.strftime(str(_('Today at %H:%S', lang)))
	    return t.strftime(str(_('On %b %d', lang)))
	else:
		return t.strftime(str(_('On %D', lang)))
    
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
def descriptionOfTransaction(tr, user, lang):
    message = ''
    if (tr.type == 'debt'):
         if (tr.fromUser == user):
             message = _('You owed %(user)s $%(amount)s', lang) % {'user': tr.toMember.userNick, 'amount': round(tr.amount, 2)}
         else:
             message = _('%(user)s owed you $%(amount)s', lang) % {'user': tr.fromMember.userNick, 'amount': round(tr.amount, 2)}
    if (tr.type == 'payment'):
         if (tr.fromUser == user):
             message = _('You paid %(user)s $%(amount)s', lang) % {'user': tr.toMember.userNick, 'amount': round(tr.amount, 2)}
         else:
             message = _('%(user)s paid you $%(amount)s', lang) % {'user': tr.fromMember.userNick, 'amount': round(tr.amount, 2)}
    if (tr.type == 'rejectedDebt'):
        if (tr.creator == user):
            if tr.fromUser == user:
                message = _('You rejected that you owed %(user)s $%(amount)s', lang) % {'user': tr.toMember.userNick, 'amount': round(tr.amount, 2)}
            else:
                message = _('You rejected that %(user)s owed you $%(amount)s', lang) % {'user': tr.toMember.userNick, 'amount': round(tr.amount, 2)}
        else:
            if tr.fromUser == user:
                message = _('%(user)s rejected that you owed him/her $%(amount)s', lang) % {'user': tr.fromMember.userNick, 'amount': round(tr.amount, 2)}
            else:
                message = _('%(user)s rejected that he/she owed you $%(amount)s', lang) % {'user': tr.fromMember.userNick, 'amount': round(tr.amount, 2)}
    if (tr.type == "rejectedPayment"):
        if (tr.creator == user):
            if tr.fromUser == user:
                message = _('You rejected that you paid %(user)s $%(amount)s', lang) % {'user': tr.toMember.userNick, 'amount': round(tr.amount, 2)}
            else:
                message = _('You rejected from %(user)s a payment of $%(amount)s', lang) % {'user': tr.toMember.userNick, 'amount': round(tr.amount, 2)}
        else:
            if tr.fromUser == user:
                message = _('%(user)s rejected that you paid him/her $%(amount)s', lang) % {'user': tr.fromMember.userNick, 'amount': round(tr.amount, 2)}
            else:
                message = _('%(user)s rejected that he/she paid you $%(amount)s', lang) % {'user': tr.fromMember.userNick, 'amount': round(tr.amount, 2)}
    if len(tr.reason) > 0:
         message += ' '
         message += _('due to %s', lang) % tr.reason
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
    
def descriptionOfBalance(balance, before, lang):
    if before:
        if balance == 0.0:
            return _('you owed no one, and no one owed you', lang)
        elif balance > 0.0:
            return _('they owed you $%s', lang) % round(abs(balance), 2)
        else:
            return _('you owed $%s', lang) % round(abs(balance), 2)
    else:
        if balance == 0.0:
            return _('you owe no one, and no one owes you', lang)
        elif balance > 0.0:
            return _('they owe you $%s', lang) % round(abs(balance), 2)
        else:
            return _('you owe $%s', lang) % round(abs(balance), 2)

def descriptionOfTotalBalance(balance, lang):
    if balance == 0.0:
        return _('You owe nobody, and nobody owes you. Hurray!', lang)
    elif balance < 0.0:
        return _('You owe a total of $%s', lang) % round(-balance, 2)
    else:
        return _('They owe you a total of $%s', lang) % round(balance, 2)
    
def descriptionOfTotalBalanceInThisGroup(balance, lang):
    if balance == 0.0:
        return _('You owe nobody, and nobody owes you in this group. Hurray!', lang)
    elif balance < 0.0:
        return _('You owe a total of $%s in this group', lang) % round(-balance, 2)
    else:
        return _('They owe you a total of $%s in this group', lang) % round(balance, 2)

def descriptionOfBalanceInGroup(membership, link, lang):
    if membership.balance < 0.0:
        return _('You owe $%(amount)s in <a href="%(link)s">%(group)s</a>', lang) % {'amount': round(-membership.balance, 2), 'group': membership.groupNick, 'link': link}
    elif membership.balance > 0.0:
        return _('They owe you $%(amount)s in <a href="%(link)s">%(group)s</a>', lang) % {'amount': round(membership.balance, 2), 'group': membership.groupNick, 'link': link}
    else:
        raise "Don't invoke this method with m.balance == 0.0"
    
def descriptionOfGeneralBalance(member, lang):
    if member.balance == 0.0:
        return _('%s owes no one, and no one owes him/her', lang) % member.userNick
    elif member.balance > 0.0:
        return _('%(user)s has $%(amount)s of credit', lang) % {'user': member.userNick, 'amount': round(member.balance, 2)}
    else:
        return _('%(user)s owes $%(amount)s', lang) % {'user': member.userNick, 'amount': round(-member.balance, 2)}