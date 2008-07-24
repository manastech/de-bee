from google.appengine.ext import db

class Group(db.Model):
	name = db.StringProperty(required=True)
    
class Membership(db.Model):
	user = db.UserProperty(required=True)
	group = db.ReferenceProperty(Group)
	balance = db.FloatProperty(required=True)
    
class Transaction(db.Model):
	creator = db.UserProperty(required=True)
	fromUser = db.UserProperty(required=True)
	toUser = db.UserProperty(required=True)
	type = db.StringProperty(required=True, choices=set(["debt", "payment", "rejectedDebt", "rejectedPayment"]))
	amount = db.FloatProperty(required=True)
	reason = db.StringProperty()
	isRejected = db.BooleanProperty()
	date = db.DateTimeProperty(auto_now=True)  
