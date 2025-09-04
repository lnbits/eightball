import json
import random
from http import HTTPStatus

from fastapi import APIRouter, Query, Request
from lnbits.core.services import create_invoice
from lnurl import (
    CallbackUrl,
    LightningInvoice,
    LnurlErrorResponse,
    LnurlPayActionResponse,
    LnurlPayMetadata,
    LnurlPayResponse,
    Max144Str,
    MessageAction,
    MilliSatoshi,
)
from pydantic import parse_obj_as

from .crud import get_eightball

eightball_lnurl_router = APIRouter()


@eightball_lnurl_router.get(
    "/api/v1/lnurl/pay/{eightball_id}",
    status_code=HTTPStatus.OK,
    name="eightball.api_lnurl_pay",
)
async def api_lnurl_pay(
    request: Request,
    eightball_id: str,
) -> LnurlPayResponse | LnurlErrorResponse:
    eightball = await get_eightball(eightball_id)
    if not eightball:
        return LnurlErrorResponse(reason="No eightball found")
    if not eightball.lnurlpayamount:
        return LnurlErrorResponse(reason="Eightball has no lnurlpayamount set")
    callback_url = str(
        request.url_for("eightball.api_lnurl_pay_callback", eightball_id=eightball_id)
    )
    return LnurlPayResponse(
        callback=parse_obj_as(CallbackUrl, callback_url),
        minSendable=MilliSatoshi(eightball.lnurlpayamount * 1000),
        maxSendable=MilliSatoshi(eightball.lnurlpayamount * 1000),
        metadata=LnurlPayMetadata(json.dumps([["text/plain", eightball.name]])),
    )


@eightball_lnurl_router.get(
    "/api/v1/lnurl/paycb/{eightball_id}",
    name="eightball.api_lnurl_pay_callback",
)
async def api_lnurl_pay_cb(
    request: Request,
    eightball_id: str,
    amount: int = Query(...),
) -> LnurlPayActionResponse | LnurlErrorResponse:
    eightball = await get_eightball(eightball_id)
    if not eightball:
        return LnurlErrorResponse(reason="No eightball found")
    random_word = random.choice(eightball.wordlist.split("\n"))
    payment = await create_invoice(
        wallet_id=eightball.wallet,
        amount=int(amount / 1000),
        memo=eightball.name,
        unhashed_description=f'[["text/plain", "{eightball.name}"]]'.encode(),
        extra={
            "tag": "EightBall",
            "eightballId": eightball_id,
            "extra": request.query_params.get("amount"),
            "word": random_word,
        },
    )
    invoice = parse_obj_as(LightningInvoice, payment.bolt11)
    action = MessageAction(message=Max144Str(random_word))
    return LnurlPayActionResponse(pr=invoice, successAction=action)
