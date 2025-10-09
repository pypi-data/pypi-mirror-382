from enum import Enum

# from shioaji.base import BaseModel

__all__ = ("Account StockAccount FutureAccount").split()


class AccountType(str, Enum):
    Stock = "S"
    Future = "F"
    H = "H"  # TODO declear


class BaseAccount:
    account_type: AccountType
    person_id: str
    broker_id: str
    account_id: str
    signed: bool = False

    def astype(self):
        return _ACCTTYPE.get(self.account_type, self.__class__)(**self.dict())


class Account(BaseAccount):
    username: str = ""
    
    def __init__(self, person_id, broker_id, account_id, signed=False, trader=''):
        self.person_id = person_id
        self.broker_id = broker_id
        self.account_id = account_id
        self.signed = signed
        self.trader = trader
    
    def __str__(self) -> str:
        return str(self.__dict__)

class StockAccount(Account):
    account_type: AccountType = AccountType.Stock


class FutureAccount(Account):
    account_type: AccountType = AccountType.Future


_ACCTTYPE = {"S": StockAccount, "F": FutureAccount}
