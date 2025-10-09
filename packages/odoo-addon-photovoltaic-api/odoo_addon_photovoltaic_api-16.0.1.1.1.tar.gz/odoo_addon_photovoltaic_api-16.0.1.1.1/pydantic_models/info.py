from . import OrmModel

class PersonType(OrmModel):
    id:   int
    name: str

class State(OrmModel):
    id:         int
    name:       str
    country_id: int

class Country(OrmModel):
    id:   int
    name: str

class Interest(OrmModel):
    id:   int
    name: str
