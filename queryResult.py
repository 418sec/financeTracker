import config
from decimal import Decimal

class TransactionQueryResult(list):
    def __init__(self, values):
        super().__init__(values)
        self.sort(key=lambda transaction: transaction.date)

    def toStr(self):
        return "\n".join(str(x) for x in self)

class AccountQueryResult():
    def __init__(self, topAccount, accountPredicate):
        self.topAccount = topAccount.clone()
        self.accountPredicate = accountPredicate

    def toStr(self, printEmptyAccounts=False, sumAllAccounts=False, factor=lambda _: 1):
        if sumAllAccounts:
            summed = sum(factor(acc) * acc.amount for acc in self.topAccount.getAllAccounts() if self.accountPredicate(acc))
            print([(acc.amount, acc.name) for acc in self.topAccount.getAllAccounts() if self.accountPredicate(acc)])
            return "{}: {}".format(self.topAccount.name, summed)
        else:
            predicate = lambda account: self.accountPredicate(account) and (printEmptyAccounts or not account.isEmpty())
            return self.accountsToStr(predicate)

    def accountsToStr(self, predicate):
        s = ""
        accountPadding = max(len(acc.name) for acc in self.topAccount.getAllAccounts())
        amountPadding = max(len(str(acc.total)) for acc in self.topAccount.getAllAccounts())
        for account in sorted(self.topAccount.getAllAccounts(), key=lambda acc: acc.name):
            if not predicate(account):
                continue
            numSpaces = account.level * 4
            indentation = numSpaces * " "
            s = s + "{:<{accountPadding}} \t {:>{amountPadding}}{currency}".format(indentation + account.rawName, str(account.total), accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency) + "\n"
        return s

    def __str__(self):
        return self.toStr()

    def getAccount(self, accountName):
        return self.topAccount.getAccount(accountName)

class BudgetResult(AccountQueryResult):
    def __init__(self, accountQueryResult, budget):
        super().__init__(accountQueryResult.topAccount, accountQueryResult.accountPredicate)
        self.budget = budget

    def accountsToStr(self, predicate):
        s = ""
        accountPadding = max(len(acc.name) for acc in self.topAccount.getAllAccounts())
        amountPadding = max(len(str(acc.total)) for acc in self.topAccount.getAllAccounts())
        for account in sorted(self.topAccount.getAllAccounts(), key=lambda acc: acc.name):
            if (not predicate(account)) or (not account.name in self.budget[config.accountsIdentifier]):
                continue
            budgetAmount = self.budget[config.accountsIdentifier][account.name]
            if budgetAmount == 0:
                percentage = 0
            else:
                percentage = account.total / budgetAmount * 100
            s = s + "{:<{accountPadding}} \t {:>{amountPadding}}{currency} / {budgetAmount}{currency} ({percentage:.0f}%)".format(account.name, account.total, accountPadding=accountPadding, amountPadding=amountPadding, currency=config.currency, budgetAmount=budgetAmount, percentage=percentage) + "\n"
        return s

