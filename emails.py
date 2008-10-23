from datetime import datetime

DeBeeEmail = "info@de-bee.com"

def transactionNoticeSubject(member):
    return "[De-Bee] Transaction notice in %s on %s" % (member.groupNick, datetime.now().strftime("%d %B %Y"))