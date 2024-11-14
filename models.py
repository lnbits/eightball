from typing import Optional

from fastapi import Request
from lnurl.core import encode as lnurl_encode
from loguru import logger
from pydantic import BaseModel


class CreateEightBallData(BaseModel):
    name: str
    description: Optional[str] = ""
    wordlist: str
    lnurlpayamount: int
    wallet: Optional[str] = None


class EightBall(BaseModel):
    id: str
    wallet: str
    name: str
    description: Optional[str] = ""
    wordlist: str
    lnurlpayamount: int

    def lnurlpay(self, req: Request) -> str:
        url = req.url_for("eightball.api_lnurl_pay", eightball_id=self.id)
        url_str = str(url)
        logger.debug(url_str)
        if url.netloc.endswith(".onion"):
            url_str = url_str.replace("https://", "http://")

        return lnurl_encode(url_str)
