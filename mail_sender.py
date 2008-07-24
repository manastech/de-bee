from google.appengine.api import mail

class MailSender:
	def sendInvitationMail(self,user_recipient, group_name, custom_invitation_text):
		subject = "You are invited to %s group!" % group_name
		body = " yeah! %s " % custom_invitation_text
		mail.send_mail("de-bee@manas.com.ar", user_recipient, subject, body)

	def sendNoticeTransaction(self,from_recipient,user_recipient, group_name, transaction):
		subject = "Transaction notice in %s group" % group_name
		body = " transaction body "
		mail.send_mail(from_recipient, user_recipient, subject, body)
        