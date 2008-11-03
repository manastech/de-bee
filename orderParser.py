from i18n import getLanguage
from i18n import _

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
		pays = _('Pays', self.lang).lower()
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
			elif firstSplits[0].strip().lower() == pays:
				if transaction.payer:
					transaction.error = self.error(linnum, _('payer has already been specified (%s)', self.lang) % transaction.payer.userNick)
					return transaction
				
				name = firstSplits[1].strip()
				member = self.getMember(members, name)
				if not member:
					transaction.error = self.error(linnum, _('member %s not found', self.lang) % name);
					return transaction
				transaction.payer = member
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
					if money == 0 or money < 0:
						transaction.error = self.error(linnum, _('invalid ammount of money (%s)', self.lang) % secondSplits[1].strip());
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
			transaction.error = _('And who pays? (Pays: ...)', self.lang)
			return transaction
		
		if len(debts) == 0:
			transaction.error = _('And what did the buy? (Someone: ...)', self.lang)
			return transaction
		
		transaction.debts = debts
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