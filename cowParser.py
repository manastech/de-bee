from i18n import getLanguage
from i18n import _

class SingleDebt:
	
	toMember = None
	money = None

class Debt:
	
	fromMember = None
	singleDebts = []

class Collaboration:

	member = None
	money = None
	
class Result:
	
	total = None
	each = None
	debts = []
	balanceChange = {}
		
class Transaction:
	
	reason = None
	collaborations = []
	cancel = False
	error = None
	
	def getTotal(self):
		total = 0.0
		for c in self.collaborations:
			total += c.money
		return total
	
	def getResult(self):
		collaborationsCopy = []
		for c in self.collaborations:
			cc = Collaboration()
			cc.member = c.member
			cc.money = c.money
			collaborationsCopy.append(cc)
		
		collaborationsCopy.sort(cmp = compareCollaborations)
		
		total = self.getTotal()
		each = total / len(collaborationsCopy)
		
		debts = []
		firstIndexWasIncremented = True
		firstIndex = 0
		lastIndex = len(collaborationsCopy) - 1		
		
		while firstIndex < lastIndex:
			fiwi = firstIndexWasIncremented
			firstIndexWasIncremented = False
			
			first = collaborationsCopy[firstIndex]
			last = collaborationsCopy[lastIndex]
			
			if first.money < each:
				if last.money > each:
					diff = min(each, min(each - first.money, last.money - each))
					
					if fiwi:
						debt = Debt()
						debt.singleDebts = []
						debt.fromMember = first.member
						debts.append(debt)
					
					singleDebt = SingleDebt()
					singleDebt.toMember = last.member
					singleDebt.money = diff
					
					debt.singleDebts.append(singleDebt)
					
					first.money = first.money + diff
					last.money = last.money - diff
					
					if first.money == each:
						firstIndex = firstIndex + 1
						firstIndexWasIncremented = True
					if last.money == each:
						lastIndex = lastIndex - 1
					
				else:
					lastIndex = lastIndex + 1 
			else:
				firstIndex = firstIndex + 1
				firstIndexWasIncremented = True
				
		result = Result()
		result.total = total
		result.each = each
		result.debts = debts
		
		result.balanceChange = {}
		for debt in debts:
			for singleDebt in debt.singleDebts:
				if not debt.fromMember in result.balanceChange:
					result.balanceChange[debt.fromMember] = -singleDebt.money
				else:
					result.balanceChange[debt.fromMember] -= singleDebt.money
					
				if not singleDebt.toMember in result.balanceChange:
					result.balanceChange[singleDebt.toMember] = singleDebt.money
				else:
					result.balanceChange[singleDebt.toMember] += singleDebt.money
		
		return result
		
def compareCollaborations(c1, c2):
	if c1.money < c2.money:
		return -1
	elif c1.money > c2.money:
		return 1
	else:
		return 0
				

class CowParser:
	
	def getMember(self, members, name):
		i = 0
		
		for member in members:
			if (member.userNick.lower() == name.lower()):
				return member
		return None
	
	def parse(self, members, string):
		reason = _('Reason', self.lang).lower()
		lines = string.split("\n")
		
		transaction = Transaction()
		collaborations = []
		
		linnum = 0
		
		for line in lines:
			linnum = linnum + 1
			
			line = line.strip()
			
			if len(line) == 0:
				continue
			
			firstSplits = line.split(':');
			
			if len(firstSplits) > 2:
				transaction.error = self.error(linnum, _('more than one colon (:) found', self.lang))
				return transaction
			
			if len(firstSplits) < 2:
				transaction.error = self.error(linnum, _('expecting colon (:)', self.lang))
				return transaction
			
			if firstSplits[0].strip().lower() == "cancel":
				if transaction.cancel:
					transaction.error = self.error(linnum, _('cancel has already been specified', self.lang))
					return transaction
				transaction.cancel = True
			elif firstSplits[0].strip().lower() == reason:
				if transaction.reason:
					transaction.error = self.error(linnum, _('reason has already been specified (%s)', self.lang) % transaction.payer.userNick)
					return transaction
				
				transaction.reason = firstSplits[1].strip()
			else:
				names = firstSplits[0].strip().split(',')
				total = len(names)
				
				for name in names:
					name = name.strip()
					
					member = self.getMember(members, name)
					if not member:
						transaction.error = self.error(linnum, _('member %s not found', self.lang) % name);
						return transaction
					
					secondSplits = firstSplits[1].split('$')
					
					if len(secondSplits) < 2:
						transaction.error = self.error(linnum, _('expecting dollar ($) for amount of money', self.lang))
						return transaction
					
					if len(secondSplits) > 2:
						transaction.error = self.error(linnum, _('more than two dollars ($) found', self.lang))
						return transaction
					
					reason = secondSplits[0].strip()
					money = float(secondSplits[1])
					if money < 0:
						transaction.error = self.error(linnum, _('invalid ammount of money (%s)', self.lang) % secondSplits[1].strip());
						return transaction
					
					money = money / total
					if total > 1:
						quantityAndReason = quantity(reason)
						reason = "%s/%s %s" % (quantityAndReason[0], total, reason)
					
					collaboration = Collaboration()
					collaboration.member = member
					collaboration.money = money
					
					collaborations.append(collaboration)
					
		if len(collaborations) == 0:
			transaction.error = _('And who are the collaborators? (Someone: ...)', self.lang)
			return transaction
		
		transaction.collaborations = collaborations
		return transaction
	
	def error(self, line, msg):
		txt = _('Error in line %s', self.lang) % line
		txt += ': '
		txt += msg
		return txt
	
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