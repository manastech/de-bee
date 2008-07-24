from google.appengine.api import mail

class MailSender:
	def sendMail(self, user_sender, user_recipient, text):
		subject = "Confirm your registration"
		body = "Man! "
		mail.send_mail("jorge@manas.com.ar", "jorge@manas.com.ar", subject, body)
        