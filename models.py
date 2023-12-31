import json
import base64
import hashlib
from collections import OrderedDict

from typing import Optional, List, Dict
from lnurl import encode as lnurl_encode  # type: ignore
from lnurl.types import LnurlPayMetadata  # type: ignore
from lnurl.models import LnurlPaySuccessAction, UrlAction  # type: ignore
from pydantic import BaseModel
from starlette.requests import Request
from .helpers import totp


class Game(BaseModel):
    id: str
    name: str
    description: str
    wallet: str
    price: int
    wordlist: str

    @classmethod
    def values(self, req: Request):
        values = self.dict()
        values["lnurl"] = lnurl_encode(
            req.url_for("eightball.lnurl_response", item_id=self.id)
        )
        return values   
    
    def lnurl(self, r: Request) -> str:
        return lnurl_encode(str(r.url_for("eightball.lnurl_response", game_id=self.id)))


    async def lnurlpay_metadata(self) -> LnurlPayMetadata:
        metadata = [["text/plain", self.description]]

        if self.image:
            metadata.append(self.image.split(":")[1].split(","))

        return LnurlPayMetadata(json.dumps(metadata))

    def success_action(
        self, wordlist: str, payment_hash: str, req: Request
    ) -> Optional[LnurlPaySuccessAction]:
        if not wordlist:
            return None

        return UrlAction(
            url=req.url_for("eightball.confirmation_code", p=payment_hash),
            description="Open to get the confirmation code for your purchase.",
        )

    def get_code(self, payment_hash: str) -> str:
        if self.method == "wordlist":
            sc = gameCounter.invoke(self)
            return sc.get_word(payment_hash)
        elif self.method == "totp":
            return totp(self.otp_key)
        return ""
    @property
    def lnurlpay_metadata(self) -> LnurlPayMetadata:
        if self.domain and self.username:
            text = f"Payment to {self.username}"
            identifier = f"{self.username}@{self.domain}"
            metadata = [["text/plain", text], ["text/identifier", identifier]]
        else:
            metadata = [["text/plain", self.description]]

        return LnurlPayMetadata(json.dumps(metadata))