#class Member:
#	
#	user = None
#
#class User:
#	
#	em = None
#		
#	def nickname(self):
#		return self.em

class Debt:

	member = None
	reason = None
	money = None
		
class Transaction:
	
	payer = None
	debts = []
	cancel = False
	error = None

class OrderParser:
	
	def getMember(self, members, name):
		i = 0
		
		for member in members:
			if (member.userNick.lower() == name.lower()):
				return member
		return None
	
	def parse(self, members, string):
		lines = string.split("\n")
		
		transaction = Transaction()
		debts = []
		
		linnum = 0
		
		for line in lines:
			linnum = linnum + 1
			
			line = line.strip()
			
			if len(line) == 0:
				continue
			
			firstSplits = line.split(':');
			
			if len(firstSplits) > 2:
				transaction.error = "Error in line %s: more than two colons (:) found" % linnum;
				return transaction
			
			if firstSplits[0].strip().lower() == "cancel":
				if transaction.cancel:
					transaction.error = "Error in line %s: cancel has already been specified " % linnum;
					return transaction
				transaction.cancel = True
			elif firstSplits[0].strip().lower() == "pays":
				if transaction.payer:
					transaction.error = "Error in line %s: payer has already been specified (%s)" % (linnum, transaction.payer.userNick);
					return transaction
				
				name = firstSplits[1].strip()
				member = self.getMember(members, name)
				if not member:
					transaction.error = "Error in line %s: member %s not found" % (linnum, name);
					return transaction
				transaction.payer = member
			else:
				names = firstSplits[0].strip().split(',')
				total = len(names)
				
				for name in names:
					name = name.strip()
					
					member = self.getMember(members, name)
					if not member:
						transaction.error = "Error in line %s: member %s not found" % (linnum, name);
						return transaction
					
					secondSplits = firstSplits[1].split('$')
					
					if len(secondSplits) < 2:
						transaction.error = "Error in line %s: expecting dollar ($) for ammount of money" % linnum;
						return transaction
					
					if len(secondSplits) > 2:
						transaction.error = "Error in line %s: more than two dollars ($) found" % linnum;
						return transaction
					
					reason = secondSplits[0].strip()
					money = float(secondSplits[1])
					if money == 0 or money < 0:
						transaction.error = "Error in line %s: invalid ammount of money (%s)" % (linnum, secondSplits[1].strip());
						return transaction
					
					money = money / total
					if total > 1:
						quantityAndReason = quantity(reason)
						
						reason = "%s/%s %s" % (quantityAndReason[0], total, reason)
					
					debt = Debt()
					debt.member = member
					debt.money = money
					debt.reason = reason
					
					debts.append(debt)
					
		if not transaction.payer:
			transaction.error = "And who pays? (Pays: ...)"
			return transaction
		
		if len(debts) == 0:
			transaction.error = "And what did the buy? (Someone: ...)"
			return transaction
		
		transaction.debts = debts
		return transaction
	
def is_numeric(char):
	return '0' <= ord(char) and ord(char) <= '9'
	
def quantity(string):
	if is_numeric(string[0]):
		quantity = 0
		while is_numeric(string[0]):
			quantity = quantity * 10 + string[0]
			string = string[1:]
			
		if string[0] == '/':
			quantity2 = 0
			
			string = string[1:]
			
			while is_numeric(string[0]):
				quantity = quantity * 10 + string[0]
				string = string[1:]
				
			if quantity2 != 0:
				quantity = quantity / quantity2
				
		elif string[0] == '.':
			quantity = quantity + '.'
			string = string[1:]
			
			while is_numeric(string[0]):
				quantity = quantity + string[0]
				string = string[1:]
			quantity = quantity + 0
			
		return [quantity, string]
	else:
		return [1, string]
	
if __name__ == '__main__':
	parser = OrderParser()
	
	u1 = User()
	u1.em = 'uno'
	
	u2 = User()
	u2.em = 'dos'
	
	u3 = User()
	u3.em = 'tres'
	
	u4 = User()
	u4.em = 'cuatro'
	
	m1 = Member()
	m1.user = u1
	
	m2 = Member()
	m2.user = u2
	
	m3 = Member()
	m3.user = u3
	
	m4 = Member()
	m4.user = u4
	
	members = [m1, m2, m3, m4]
	
	transaction = parser.parse(members, "Pays: uno\ndos: algo $5\ntres, cuatro: algo mas $12\nuno: foo, bar, baz $20")
	
	print '======================'
	
	if transaction.error:
		print transaction.error
	else:
		print "Payer: %s" % transaction.payer.userNick
		print "Cancel: %s" % transaction.cancel
		for debt in transaction.debts:
			print "%s bought '%s' for $%s" % (debt.member.userNick, debt.reason, debt.money)
	