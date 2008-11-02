from google.appengine.api import mail
from datetime import datetime
from io import readFile
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
                'html': '<b>%s</b> told me that <b style="color:#005E00">he/she owed you $%s</b> because of %s.' 
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
                'html': '<b>%s</b> told me that <b style="color:#5C0101">you owed him/her $%s</b> because of %s.' 
                }
    
def someonePayedYou(reject = False):
    if reject:
        return {
                'txt': '%s rejected a transaction that said that he/she paid you $%s because of %s.',
                'html': '%s rejected a transaction that said that he/she paid you $%s because of %s.' 
                }
    else:
        return {
                'txt': '%s told me that he/she paid you $%s because of %s.',
                'html': '<b>%s</b> told me that <b style="color:#5C0101">he/she paid you $%s</b> because of %s.' 
                }
    
def youPayedSomeone(reject = False):
    if reject:
        return {
                'txt': '%s rejected a transaction that said that you paid him/her $%s because of %s.',
                'html': '%s rejected a transaction that said that you paid him/her $%s because of %s.' 
                }
    else:
        return {
                'txt': '%s told me that you paid him/her $%s because of %s.',
                'html': '<b>%s</b> told me that <b style="color:#005E00">you paid him/her $%s</b> because of %s.' 
                }
def creatorSaysYouOwedSomeone():
    return {
            'txt': '%s told me that you owed %s $%s because of %s.',
            'html': '<b>%s told me</b> that <b style="color:#5C0101">you owed %s $%s</b> because of %s.'
            }

def createActionMail(me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, mailBody):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
    message.body = actionMessageTxt(me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['txt'])
    message.html = actionMessageHtml(me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['html'])
    return message

def createRejectionMail(me, someone, tr, reason, balanceBefore, balanceNow, mailBody):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
    message.body = rejectionMessageTxt(me, someone, tr, reason,  balanceBefore, balanceNow, mailBody['txt'])
    message.html = rejectionMessageHtml(me, someone, tr, reason,  balanceBefore, balanceNow, mailBody['html'])
    return message

def createThirdPartyActionMail(creator, me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, mailBody):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone))
    message.body = thirdPartyActionMessageTxt(creator, me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['txt'])
    message.html = thirdPartyActionMessageHtml(creator, me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['html'])
    return message

def createBulkMail(transaction, creatorMember, balanceBefore, balanceNow):
    debtorsTxt = ''
    debtorsHtml = '<ul>'
    
    total = 0.0
    
    for debt in transaction.debts:
    	if creatorMember.user != debt.member.user:
	        debtorsTxt += ' * $%s to %s because of %s\n' % (debt.money, debt.member.userNick, debt.reason)
	        debtorsHtml += '<li>$%s to %s because of %s</li>' % (debt.money, debt.member.userNick, debt.reason)
	        total += debt.money
        
    debtorsHtml += '</ul>'
    
    # Try send email to the debtor
    message = mail.EmailMessage(
                    sender = DeBeeEmail,
                    to = transaction.payer.user.email(), 
                    subject = transactionNoticeSubject(transaction.payer))
    
    message.body = readFile('texts/creator_says_you_payed_for_them.txt') % (transaction.payer.userNick, creatorMember.userNick, debtorsTxt, total, descriptionOfBalance(balanceBefore, before = True), transaction.payer.groupNick, descriptionOfBalance(balanceNow, before = False))
    message.html = readFile('texts/creator_says_you_payed_for_them.html') % (transaction.payer.userNick, creatorMember.userNick, debtorsHtml, total, descriptionOfBalanceHtml(balanceBefore, before = True), transaction.payer.groupNick, descriptionOfBalanceHtml(balanceNow, before = False))
    return message

def actionMessageTxt(me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body):
    realBody = body % (me.userNick, amount, reason)
    
    global actionTxt
    if actionTxt is None:
        actionTxt = readFile('texts/action.txt')
         
    return actionTxt % (someone.userNick, realBody, descriptionOfBalance(balanceBefore, before = True), someone.groupNick, descriptionOfBalance(balanceNow, before = False), rejectUrl)

def actionMessageHtml(me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body):
    realBody = body % (me.userNick, amount, reason)
    
    global actionHtml
    if actionHtml is None:
        actionHtml = readFile('texts/action.html')
        
    return actionHtml % (someone.userNick, realBody, descriptionOfBalanceHtml(balanceBefore, before = True), someone.groupNick, descriptionOfBalanceHtml(balanceNow, before = False), rejectUrl)

def rejectionMessageTxt(me, someone, tr, reason, balanceBefore, balanceNow, body):
    if reason != "":
        reason = '\n%s\n' % reason
    
    realBody = body % (me.userNick, tr.amount, tr.reason)
    
    global rejectionTxt
    if rejectionTxt is None:
        rejectionTxt = readFile('texts/rejection.txt')
        
    return rejectionTxt % (someone.userNick, realBody, reason, descriptionOfBalance(balanceBefore, before = True), someone.groupNick, descriptionOfBalance(balanceNow, before = False))

def rejectionMessageHtml(me, someone, tr, reason, balanceBefore, balanceNow, body):
    if reason != "":
        reason = '%s<br><br>' % reason
    
    realBody = body % (me.userNick, tr.amount, tr.reason)
    
    global rejectionHtml
    if rejectionHtml is None:
        rejectionHtml = readFile('texts/rejection.html')
        
    return rejectionHtml % (someone.userNick, realBody, reason, descriptionOfBalanceHtml(balanceBefore, before = True), someone.groupNick, descriptionOfBalanceHtml(balanceNow, before = False))

def thirdPartyActionMessageTxt(creator, me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body):
    realBody = body % (creator.userNick, me.userNick, amount, reason)
    
    global actionTxt
    if actionTxt is None:
        actionTxt = readFile('texts/action.txt')
         
    return actionTxt % (someone.userNick, realBody, descriptionOfBalance(balanceBefore, before = True), someone.groupNick, descriptionOfBalance(balanceNow, before = False), rejectUrl)
    
def thirdPartyActionMessageHtml(creator, me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body):
    realBody = body % (creator.userNick, me.userNick, amount, reason)
    
    global actionHtml
    if actionHtml is None:
        actionHtml = readFile('texts/action.html')
        
    return actionHtml % (someone.userNick, realBody, descriptionOfBalanceHtml(balanceBefore, before = True), someone.groupNick, descriptionOfBalanceHtml(balanceNow, before = False), rejectUrl)

def transactionNoticeSubject(member):
    return "[De-Bee] Transaction notice in %s on %s" % (member.groupNick, datetime.now().strftime("%d %B %Y"))
   
def descriptionOfBalanceHtml(balance, before):
	desc = descriptionOfBalance(balance, before)
	if balance > 0.0:
		desc = '<span style="color:#005E00">%s</span>' % desc
	elif balance < 0.0:
		desc = '<span style="color:#5C0101">%s</span>' % desc
	return desc

def sendEmail(email):
    try:
        email.send()
    except:
        iHateGoogleAppEngineMailQuotaRules = True