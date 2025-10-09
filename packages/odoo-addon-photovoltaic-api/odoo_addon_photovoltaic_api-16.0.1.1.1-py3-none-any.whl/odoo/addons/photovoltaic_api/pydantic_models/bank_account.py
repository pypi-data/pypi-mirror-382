from . import OrmModel

class BankAccountIn(OrmModel):
    acc_number: str

class BankAccountOut(OrmModel):
    id:         int
    acc_number: str
