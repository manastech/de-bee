from google.appengine.ext import db

class Group(db.Model):
	name = db.StringProperty(required=True)
    
class Membership(db.Model):
	user = db.UserProperty(required=True)
	group = db.ReferenceProperty(Group)
	balance = db.FloatProperty(required=True)
	
	# The alias of the group name
	alias = db.StringProperty()
	
	# The nickname of the user in the group
	nickname = db.StringProperty()
	
	# The alias of the group name, or the group name if the
	# alias is not defined
	@property
	def name(self):
		if self.alias and self.alias != "":
			return self.alias
		else:
			return self.group.name
		
	# The nickname of the user in the group, or the user's nickname
	# if the membership's nickname is not defined 
	@property
	def nick(self):
		if self.nickname and self.nickname != "":
			return self.nickname
		else:
			return self.user.nickname()
    
class Transaction(db.Model):
	group = db.ReferenceProperty(Group)
	type = db.StringProperty(required=True, choices=set(["debt", "payment", "rejectedDebt", "rejectedPayment"]))
	amount = db.FloatProperty(required=True)
	reason = db.StringProperty()
	isRejected = db.BooleanProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	
	creatorMember = db.ReferenceProperty(Membership, collection_name="creatorMember_collection_name")
	fromMember = db.ReferenceProperty(Membership, collection_name="fromMember_collection_name")
	toMember = db.ReferenceProperty(Membership, collection_name="toMember_collection_name")
	
	updated = db.BooleanProperty()
	
	@property
	def creator(self):
		if self.creatorMember:
			return self.creatorMember.user
		else:
			return None
	
	@property
	def fromUser(self):
		if self.fromMember:
			return self.fromMember.user
		else:
			return None
	
	@property
	def toUser(self):
		if self.toMember:
			return self.toMember.user
		else:
			return None