from google.appengine.ext import db
from hashlib import sha224

class Group(db.Model):
	name = db.StringProperty(required=True)
	
	# All memberships of a group in no particular order
	@property
	def memberships(self):
		ret = Membership.gql("WHERE group = :1", self)
		return ret.fetch(10000)
    
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
	def groupNick(self):
		if self.alias and self.alias != "":
			return self.alias
		else:
			return self.group.name
		
	# The nickname of the user in the group, or the user's nickname
	# if the membership's nickname is not defined 
	@property
	def userNick(self):
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
		
	@property
	def hash(self):
		m = sha224()
		m.update(str(self.key()))
		m.update(self.creator.email())
		m.update(self.fromUser.email())
		m.update(self.toUser.email())
		m.update(self.type)
		m.update(str(self.date))
		return m.hexdigest()
	
	def isValidHash(self, hash):
		return self.hash == hash
	
	def getCompensateFor(self, user):
		if user == self.fromUser:
			creatorMember = self.fromMember
		else:
			creatorMember = self.toMember
        
		return Transaction(
			group = self.group,
			type = self.getCompensateType(self.type),
			amount = self.amount,
		    reason = self.reason,
		    isRejected = False,
		    creatorMember = creatorMember,
		    fromMember = self.fromMember,
		    toMember = self.toMember 
		    )
		
	def getCompensateType(self, type):
		if type == 'debt':
			return 'rejectedDebt'
		else:
			return 'rejectedPayment'