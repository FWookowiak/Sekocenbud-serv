import datetime
from pydantic import BaseModel

class InkosToken(BaseModel):
    name: str
    token: str
    expiration_date: datetime
    call_count: int

class DBF_Base(BaseModel):
    katalog: str
    symbol: str
    opis: str
    jm_nazwa: str
    cena_sr: int

class DBF_Create(DBF_Base):
    pass

class DBF(DBF_Base):
    id: int

    class Config:
        orm_mode = True
