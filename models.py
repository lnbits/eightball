from typing import Optional

from pydantic import BaseModel


class CreateEightBallData(BaseModel):
    name: str
    wordlist: str
    lnurlpayamount: int
    wallet: Optional[str] = None


class EightBall(BaseModel):
    id: str
    wallet: str
    name: str
    wordlist: str
    lnurlpayamount: int
    lnurlpay: Optional[str]
