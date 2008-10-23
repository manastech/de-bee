from model import Membership
from datetime import datetime
from re import compile

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

# Reads the entire contents of a file, given its path
def readFile(path):
    f = open(path)
    text = f.read()
    f.close()
    return text

# Returns the description of a transaction according to
# a users's point of view. This does not include the date
# of the transaction.
def descriptionOfTransaction(tr, user):
    message = ''
    if (tr.type == "debt"):
         if (tr.fromUser == user):
             message = "You owed " + tr.toMember.userNick + " $" + str(tr.amount)
         else:
             message = tr.fromMember.userNick + " owed you $" + str(tr.amount)
    if (tr.type == "payment"):
         if (tr.fromUser == user):
             message = "You payed " + tr.toMember.userNick + " $" + str(tr.amount)
         else:
             message = tr.fromMember.userNick + " payed you $" + str(tr.amount)
    if (tr.type == "rejectedDebt"):
        if (tr.creator == user):
            if tr.fromUser == user:
                message = "You rejected that you owed " + tr.toMember.userNick + " $" + str(tr.amount)
            else:
                message = "You rejected that " + tr.toMember.userNick + " owed you $" + str(tr.amount)
        else:
            if tr.fromUser == user:
                message = tr.fromMember.userNick + " rejected that you owed him/her $" + str(tr.amount)
            else:
                message = tr.fromMember.userNick + " rejected that he/she owed you $" + str(tr.amount)
    if (tr.type == "rejectedPayment"):
        if (tr.creator == user):
            if tr.fromUser == user:
                message = "You rejected that you payed " + tr.toMember.userNick + " $" + str(tr.amount)
            else:
                message = "2You rejected from " + tr.toMember.userNick + " a payment of $" + str(tr.amount)
        else:
            if tr.fromUser == user:
                message = tr.fromMember.userNick + " rejected that you payed him/her $" + str(tr.amount)
            else:
                message = tr.fromMember.userNick + " rejected that he/she payed you $" + str(tr.amount)
    if len(tr.reason) > 0:
         message = message + " due to " + tr.reason
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