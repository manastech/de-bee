from google.appengine.api import mail
from datetime import datetime
from io import readFile
from util import descriptionOfBalance
from i18n import _

DeBeeEmail = "info@de-bee.com"
actionTxt = {}
actionHtml = {}
rejectionTxt = {}
rejectionHtml = {}
bulkTxt = {}
bulkHtml = {}
cowTxt = {}
cowHtml = {}

def someoneOwedYou(lang, reject = False):
    if reject:
        return {
                'txt': _('%(user)s rejected a transaction that said that he/she owed you $%(amount)s because of %(reason)s.', lang),
                'html': _('%(user)s rejected a transaction that said that he/she owed you $%(amount)s because of %(reason)s.', lang) 
                }
    else:
        return {
                'txt': _('%(user)s said that he/she owed you $%(amount)s because of %(reason)s.', lang),
                'html': _('<b>%(user)s</b> said that <b style="color:#005E00">he/she owed you $%(amount)s</b> because of %(reason)s.', lang) 
                }
    
def youOwedSomeone(lang, reject = False):
    if reject:
        return {
                'txt': _('%(user)s rejected a transaction that said that you owed him/her $%(amount)s because of %(reason)s.', lang),
                'html': _('%(user)s rejected a transaction that said that you owed him/her $%(amount)s because of %(reason)s.', lang) 
                }
    else:
        return {
                'txt': _('%(user)s said that you owed him/her $%(amount)s because of %(reason)s.', lang),
                'html': _('<b>%(user)s</b> said that <b style="color:#5C0101">you owed him/her $%(amount)s</b> because of %(reason)s.', lang) 
                }
    
def someonePayedYou(lang, reject = False):
    if reject:
        return {
                'txt': _('%(user)s rejected a transaction that said that he/she paid you $%(amount)s because of %(reason)s.', lang),
                'html': _('%(user)s rejected a transaction that said that he/she paid you $%(amount)s because of %(reason)s.', lang) 
                }
    else:
        return {
                'txt': _('%(user)s said that he/she paid you $%(amount)s because of %(reason)s.', lang),
                'html': _('<b>%(user)s</b> said that <b style="color:#5C0101">he/she paid you $%(amount)s</b> because of %(reason)s.', lang) 
                }
    
def youPayedSomeone(lang, reject = False):
    if reject:
        return {
                'txt': _('%(user)s rejected a transaction that said that you paid him/her $%(amount)s because of %(reason)s.', lang),
                'html': _('%(user)s rejected a transaction that said that you paid him/her $%(amount)s because of %(reason)s.', lang) 
                }
    else:
        return {
                'txt': _('%(user)s said that you paid him/her $%(amount)s because of %(reason)s.', lang),
                'html': _('<b>%(user)s</b> said that <b style="color:#005E00">you paid him/her $%(amount)s</b> because of %(reason)s.', lang) 
                }
def creatorSaysYouOwedSomeone(lang):
    return {
            'txt': _('%(creator)s said that you owed %(user)s $%(amount)s because of %(reason)s.', lang),
            'html': _('<b>%(creator)s said</b> that <b style="color:#5C0101">you owed %(user)s $%(amount)s</b> because of %(reason)s.', lang)
            }

def createActionMail(me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, mailBody, lang):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone, lang))
    message.body = actionMessageTxt(me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['txt'], lang)
    message.html = actionMessageHtml(me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['html'], lang)
    return message

def createRejectionMail(me, someone, tr, reason, balanceBefore, balanceNow, mailBody, lang):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone, lang))
    message.body = rejectionMessageTxt(me, someone, tr, reason,  balanceBefore, balanceNow, mailBody['txt'], lang)
    message.html = rejectionMessageHtml(me, someone, tr, reason,  balanceBefore, balanceNow, mailBody['html'], lang)
    return message

def createThirdPartyActionMail(creator, me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, mailBody, lang):
    message = mail.EmailMessage(
                            sender = DeBeeEmail, 
                            to = someone.user.email(), 
                            subject = transactionNoticeSubject(someone, lang))
    message.body = thirdPartyActionMessageTxt(creator, me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['txt'], lang)
    message.html = thirdPartyActionMessageHtml(creator, me, someone, amount, reason,  balanceBefore, balanceNow, rejectUrl, mailBody['html'], lang)
    return message

def createBulkMail(transaction, creatorMember, balanceBefore, balanceNow, lang):
    debtorsTxt = ''
    debtorsHtml = '<ul>'
    item = _('$%s to %s because of %s', lang)
    itemTxt = ' * %s\n' % item
    itemHtml = '<li>%s</li>' % item
    
    total = 0.0
    
    for debt in transaction.debts:
    	if transaction.payer.user != debt.member.user:
	        debtorsTxt += itemTxt % (round(debt.money, 2), debt.member.userNick, debt.reason)
	        debtorsHtml += itemHtml % (round(debt.money, 2), debt.member.userNick, debt.reason)
	        total += debt.money
        
    debtorsHtml += '</ul>'
    
    # Try send email to the debtor
    message = mail.EmailMessage(
                    sender = DeBeeEmail,
                    to = transaction.payer.user.email(), 
                    subject = transactionNoticeSubject(transaction.payer, lang))
    
    global bulkTxt
    if not (lang in bulkTxt):
        bulkTxt[lang] = readFile('texts/%s/creator_says_you_payed_for_them.txt' % lang)
        
    global bulkHtml
    if not (lang in bulkHtml):
        bulkHtml[lang] = readFile('texts/%s/creator_says_you_payed_for_them.html' % lang)  
    
    message.body = bulkTxt[lang] % (transaction.payer.userNick, creatorMember.userNick, debtorsTxt, round(total, 2), descriptionOfBalance(balanceBefore, True, lang), transaction.payer.groupNick, descriptionOfBalance(balanceNow, False, lang))
    message.html = bulkHtml[lang] % (transaction.payer.userNick, creatorMember.userNick, debtorsHtml, round(total, 2), descriptionOfBalanceHtml(balanceBefore, True, lang), transaction.payer.groupNick, descriptionOfBalanceHtml(balanceNow, False, lang))
    return message

def createCowMail(creatorMember, transaction, result, toMember, balanceBefore, balanceNow, lang):
    message = mail.EmailMessage(
                    sender = DeBeeEmail,
                    to = toMember.user.email(),
                    subject = transactionNoticeSubject(toMember, lang))
    
    global cowTxt
    if not (lang in cowTxt):
        cowTxt[lang] = readFile('texts/%s/cow.txt' % lang)
        
    global cowHtml
    if not (lang in cowHtml):
        cowHtml[lang] = readFile('texts/%s/cow.html' % lang)
        
    otherMembers = []
    for member, balance in result.balanceChange.iteritems():
         if member.user != toMember.user:
             otherMembers.append(member)
             
    others = ''
    i = 0
    for member in otherMembers:
        if i == len(otherMembers) - 1:
            others += ' '
            others += _('and', lang)
            others += ' '
        elif i != 0:
            others += ', '        
        others += member.userNick
        i = i + 1
    
    contributorsTxt = ''
    contributorsHtml = '<ul>'
    
    for col in transaction.collaborations:
        if col.money > 0:
            if col.member.user == toMember.user:
                mem = _('You', lang)
            else:
                mem = col.member.userNick
            contributorsTxt += ' * %s: $%s\n' % (mem, round(col.money, 2))
            contributorsHtml += '<li>%s: $%s</li>' % (mem, round(col.money, 2))
            
    contributorsHtml += '</ul>'
            
    decisionTxt = ''
    decisionHtml = '<ul>'
            
    for debt in result.debts:
        i = 0
        msg = ''
        for singleDebt in debt.singleDebts:
            tuple = { 'from': debt.fromMember.userNick, 'to': singleDebt.toMember.userNick, 'amount': round(singleDebt.money, 2) }
            if i == 0:
                if debt.fromMember.user == toMember.user:
                    msg += _('You owe %(to)s $%(amount)s', lang) % tuple
                elif singleDebt.toMember.user == toMember.user:
                    msg += _('%(from)s owes you $%(amount)s', lang) % tuple
                else:
                    msg += _('%(from)s owes %(to)s $%(amount)s', lang) % tuple
            elif i < len(debt.singleDebts) - 1:
                msg += ', '
                if singleDebt.toMember.user == toMember.user:
                    msg += _('you $%(amount)s', lang) % tuple
                else:
                    msg += _('%(to)s $%(amount)s', lang) % tuple
            else:
                msg += ' '
                msg += _('and', lang)
                msg += ' '
                if singleDebt.toMember.user == toMember.user:
                    msg += _('you $%(amount)s', lang) % tuple
                else:
                    msg += _('%(to)s $%(amount)s', lang) % tuple
            i = i + 1
        decisionTxt += ' * %s\n' % msg
        decisionHtml += '<li>%s</li>' % msg
        
    decisionHtml += '</ul>'
        
    message.body = cowTxt[lang] % (toMember.userNick, creatorMember.userNick, transaction.reason, others, round(result.total, 2), round(result.each, 2), contributorsTxt, decisionTxt, descriptionOfBalance(balanceBefore, True, lang), toMember.groupNick, descriptionOfBalance(balanceNow, False, lang))
    message.html = cowHtml[lang] % (toMember.userNick, creatorMember.userNick, transaction.reason, others, round(result.total, 2), round(result.each, 2), contributorsHtml, decisionHtml, descriptionOfBalanceHtml(balanceBefore, True, lang), toMember.groupNick, descriptionOfBalanceHtml(balanceNow, False, lang))    
    return message

def actionMessageTxt(me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body, lang):
    realBody = body % {'user': me.userNick, 'amount': amount, 'reason': reason}
    
    global actionTxt
    if not (lang in actionTxt):
        actionTxt[lang] = readFile('texts/%s/action.txt' % lang)
    
    return actionTxt[lang] % (someone.userNick, realBody, 
                              descriptionOfBalance(balanceBefore, True, lang), someone.groupNick, 
                              descriptionOfBalance(balanceNow, False, lang), rejectUrl)

def actionMessageHtml(me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body, lang):
    realBody = body % {'user': me.userNick, 'amount': amount, 'reason': reason}
    
    global actionHtml
    if not (lang in actionHtml):
        actionHtml[lang] = readFile('texts/%s/action.html' % lang)
        
    return actionHtml[lang] % (someone.userNick, realBody, descriptionOfBalanceHtml(balanceBefore, True, lang), someone.groupNick, descriptionOfBalanceHtml(balanceNow, False, lang), rejectUrl)

def rejectionMessageTxt(me, someone, tr, reason, balanceBefore, balanceNow, body, lang):
    if reason != "":
        reason = '\n%s\n' % reason
    
    realBody = body % {'user': me.userNick, 'amount': tr.amount, 'reason': tr.reason}
    
    global rejectionTxt
    if not (lang in rejectionTxt):
        rejectionTxt[lang] = readFile('texts/%s/rejection.txt' % lang)
        
    return rejectionTxt[lang] % (someone.userNick, realBody, reason, descriptionOfBalance(balanceBefore, True, lang), someone.groupNick, descriptionOfBalance(balanceNow, False, lang))

def rejectionMessageHtml(me, someone, tr, reason, balanceBefore, balanceNow, body, lang):
    if reason != "":
        reason = '%s<br><br>' % reason
    
    realBody = body % {'user': me.userNick, 'amount': tr.amount, 'reason': tr.reason}
    
    global rejectionHtml
    if not (lang in rejectionHtml):
        rejectionHtml[lang] = readFile('texts/%s/rejection.html' % lang)
        
    return rejectionHtml[lang] % (someone.userNick, realBody, reason, descriptionOfBalanceHtml(balanceBefore, True, lang), someone.groupNick, descriptionOfBalanceHtml(balanceNow, False, lang))

def thirdPartyActionMessageTxt(creator, me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body, lang):
    realBody = body % {'creator': creator.userNick, 'user': me.userNick, 'amount': amount, 'reason': reason}
    
    global actionTxt
    if not (lang in actionTxt):
        actionTxt[lang] = readFile('texts/%s/action.txt' % lang)
         
    return actionTxt[lang] % (someone.userNick, realBody, descriptionOfBalance(balanceBefore, True, lang), someone.groupNick, descriptionOfBalance(balanceNow, False, lang), rejectUrl)
    
def thirdPartyActionMessageHtml(creator, me, someone, amount, reason, balanceBefore, balanceNow, rejectUrl, body, lang):
    realBody = body % {'creator': creator.userNick, 'user': me.userNick, 'amount': amount, 'reason': reason}
    
    global actionHtml
    if not (lang in actionHtml):
        actionHtml[lang] = readFile('texts/%s/action.html' % lang)
        
    return actionHtml[lang] % (someone.userNick, realBody, descriptionOfBalanceHtml(balanceBefore, True, lang), someone.groupNick, descriptionOfBalanceHtml(balanceNow, False, lang), rejectUrl)

def transactionNoticeSubject(member, lang):
    return _('[De-Bee] Transaction notice in %s on %s', lang) % (member.groupNick, datetime.now().strftime("%d %B %Y"))
   
def descriptionOfBalanceHtml(balance, before, lang):
	desc = descriptionOfBalance(balance, before, lang)
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