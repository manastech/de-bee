from google.appengine.api import mail
from datetime import datetime
from util import readFile
from util import descriptionOfBalance

DeBeeEmail = "info@de-bee.com"
actionTxt = None
actionHtml = None
rejectionTxt = None
rejectionHtml = None

def someoneOwedYou(reject = False):
    if reject:
        return {
                'txt': '%s rejected a transaction that said that he/she owed you $%s because of %s.',
                'html': '%s rejected a transaction that said that he/she owed you $%s because of %s.' 
                }
    else:
        return {
                'txt': '%s told me that he/she owed you $%s because of %s.',
                'html': '<b>%s</b> told me that <b>he/she owed you $%s</b> because of %s.' 
                }
    
def youOwedSomeone(reject = False):
    if reject:
        return {
                'txt': '%s rejected a transaction that said that you owed him/her $%s because of %s.',
                'html': '%s rejected a transaction that said that you owed him/her $%s because of %s.', 
                }
    else:
        return {
                'txt': '%s told me that you owed him/her $%s because of %s.',
                'html': '<b>%s</b> told me that <b>you owed him/her $%s</b> because of %s.' 
                }
    
def someonePayedYou(reject = False):
    if reject:
        return {
                'txt': '%s rejected a transaction that said that he/she payed you $%s because of %s.',
                'html': '%s rejected a transaction that said that he/she payed you $%s because of %s.' 
                }
    else:
        return {
                'txt': '%s told me that he/she payed you $%s because of %s.',
                'html': '<b>%s</b> told me that <b>he/she payed you $%s</b> because of %s.' 
                }
    
def youPayedSomeone(reject = False):
    if reject:
        return {
                'txt': '%s rejected a transaction that said that you payed him/her $%s because of %s.',
                'html': '%s rejected a transaction that said that you payed him/her $%s because of %s.' 
                }
    else:
        return {
                'txt': '%s told me that you payed him/her $%s because of %s.',
                'html': '<b>%s</b> told me that <b>you payed him/her $%s</b> because of %s.' 
                }
def creatorSaysYouOwedSomeone():
    return {
            'txt': '%s told me that you owe %s $%s because of %s.',
            'html': '<b>%s<b> told me that <b>you owe %s $%s<b> because of %s.'
            }

def createActionMail(me, someone, amount, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, mailBody):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
    message.body = actionMessageTxt(me, someone, amount, reason,  descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, mailBody['txt'])
    message.html = actionMessageHtml(me, someone, amount, reason,  descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, mailBody['html'])
    return message

def createRejectionMail(me, someone, tr, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, mailBody):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
    message.body = rejectionMessageTxt(me, someone, tr, reason,  descriptionOfBalanceBefore, descriptionOfBalanceNow, mailBody['txt'])
    message.html = rejectionMessageHtml(me, someone, tr, reason,  descriptionOfBalanceBefore, descriptionOfBalanceNow, mailBody['html'])
    return message

def createThirdPartyActionMail(creator, me, someone, amount, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, mailBody):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
    message.body = thirdPartyActionMessageTxt(creator, me, someone, amount, reason,  descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, mailBody['txt'])
    message.html = thirdPartyActionMessageHtml(creator, me, someone, amount, reason,  descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, mailBody['html'])
    return message

def createBulkMail(transaction, creatorMember, descriptionOfPayersBalanceBefore, descriptionOfPayersBalanceNow):
    descriptionOfPayersBalanceNow = descriptionOfBalance(transaction.payer, before = False)
    
    debtorsTxt = ''
    debtorsHtml = '<ul>'
    
    total = 0.0
    
    for debt in transaction.debts:
        debtorsTxt += ' * $%s to %s because of %s\n' % (debt.money, debt.member.userNick, debt.reason)
        debtorsHtml += '<li>$%s to %s because of %s</li>' % (debt.money, debt.member.userNick, debt.reason)
        total += debt.money
        
    debtorsHtml += '</ul>'
    
    # Try send email to the debtor
    message = mail.EmailMessage(
                    sender = DeBeeEmail,
                    to = transaction.payer.user.email(), 
                    subject = transactionNoticeSubject(transaction.payer))
    
    message.body = readFile('texts/creator_says_you_payed_for_them.txt') % (transaction.payer.userNick, creatorMember.userNick, debtorsTxt, total, descriptionOfPayersBalanceBefore, transaction.payer.groupNick, descriptionOfPayersBalanceNow)
    message.html = readFile('texts/creator_says_you_payed_for_them.html') % (transaction.payer.userNick, creatorMember.userNick, debtorsHtml, total, descriptionOfPayersBalanceBefore, transaction.payer.groupNick, descriptionOfPayersBalanceNow)
    return message

def actionMessageTxt(me, someone, amount, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, body):
    realBody = body % (me.userNick, amount, reason)
    
    global actionTxt
    if actionTxt is None:
        actionTxt = readFile('texts/action.txt')
         
    return actionTxt % (someone.userNick, realBody, descriptionOfBalanceBefore, someone.groupNick, descriptionOfBalanceNow, rejectUrl)

def actionMessageHtml(me, someone, amount, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, body):
    realBody = body % (me.userNick, amount, reason)
    
    global actionHtml
    if actionHtml is None:
        actionHtml = readFile('texts/action.html')
        
    return actionHtml % (someone.userNick, realBody, descriptionOfBalanceBefore, someone.groupNick, descriptionOfBalanceNow, rejectUrl)

def rejectionMessageTxt(me, someone, tr, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, body):
    if reason != "":
        reason = '\n%s\n' % reason
    
    realBody = body % (me.userNick, tr.amount, tr.reason)
    
    global rejectionTxt
    if rejectionTxt is None:
        rejectionTxt = readFile('texts/rejection.txt')
        
    return rejectionTxt % (someone.userNick, realBody, reason, descriptionOfBalanceBefore, someone.groupNick, descriptionOfBalanceNow)

def rejectionMessageHtml(me, someone, tr, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, body):
    if reason != "":
        reason = '%s<br><br>' % reason
    
    realBody = body % (me.userNick, tr.amount, tr.reason)
    
    global rejectionHtml
    if rejectionHtml is None:
        rejectionHtml = readFile('texts/rejection.html')
        
    return rejectionHtml % (someone.userNick, realBody, reason, descriptionOfBalanceBefore, someone.groupNick, descriptionOfBalanceNow)

def thirdPartyActionMessageTxt(creator, me, someone, amount, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, body):
    realBody = body % (creator.userNick, me.userNick, amount, reason)
    
    global actionTxt
    if actionTxt is None:
        actionTxt = readFile('texts/action.txt')
         
    return actionTxt % (someone.userNick, realBody, descriptionOfBalanceBefore, someone.groupNick, descriptionOfBalanceNow, rejectUrl)
    
def thirdPartyActionMessageHtml(creator, me, someone, amount, reason, descriptionOfBalanceBefore, descriptionOfBalanceNow, rejectUrl, body):
    realBody = body % (creator.userNick, me.userNick, amount, reason)
    
    global actionHtml
    if actionHtml is None:
        actionHtml = readFile('texts/action.html')
        
    return actionHtml % (someone.userNick, realBody, descriptionOfBalanceBefore, someone.groupNick, descriptionOfBalanceNow, rejectUrl)

def transactionNoticeSubject(member):
    return "[De-Bee] Transaction notice in %s on %s" % (member.groupNick, datetime.now().strftime("%d %B %Y"))

def sendEmail(email):
    try:
        email.send()
    except:
        iHateGoogleAppEngineMailQuotaRules = True