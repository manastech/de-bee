# Compares two Transaction objects by date.
# First comes the transaction that has the most recent date.
def compareTransactionsByDateDesc(x, y):
    if x.date > y.date:
        return -1
    elif x.date < y.date:
         return 1
    else:
        return 0

# Compares two Memmbership objects by userNick.
# First comes the nicks that are lexicographically first.
def compareMembershipsByUserNick(x, y):
    if x.userNick.lower() < y.userNick.lower():
        return -1
    elif x.userNick.lower() > y.userNick.lower():
         return 1
    else:
        return 0

# Compares two Membership objects by groupNick.
# First comes the groupNicks that are lexicographically first.
def compareMembershipsByGroupNick(x, y):
    if x.groupNick.lower() < y.groupNick.lower():
        return -1
    elif x.groupNick.lower() > y.groupNick.lower():
         return 1
    else:
        return 0
    
# Compares two Memmbership objects by balance.
# First comes the balances that are lower.
def compareMembershipsByBalance(x, y):
    if x.balance < y.balance:
        return -1
    elif x.balance > y.balance:
         return 1
    else:
        return 0
    
# Compares two Memmbership objects by balance, descendantly.
# First comes the balances that are higher.
def compareMembershipsByBalanceDesc(x, y):
    return -compareMembershipsByBalance(x, y)