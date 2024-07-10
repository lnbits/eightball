from sqlite3 import Row
from typing import Optional
from pydantic import BaseModel


class CreateEightBallData(BaseModel):
    wallet: Optional[str]
    name: Optional[str]
    wordlist: Optional[str]
    lnurlpayamount: Optional[int]


class EightBall(BaseModel):
    id: str
    wallet: Optional[str]
    name: Optional[str]
    wordlist: Optional[str]
    lnurlpayamount: Optional[int]
    lnurlpay: Optional[str]

    @classmethod
    def from_row(cls, row: Row) -> "EightBall":
        return cls(**dict(row))
