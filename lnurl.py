from http import HTTPStatus
from fastapi import Query, Request
from . import eightball_ext
from .crud import get_eightball
from lnbits.core.services import create_invoice
from loguru import logger
import random


@eightball_ext.get(
    "/api/v1/lnurl/pay/{eightball_id}",
    status_code=HTTPStatus.OK,
    name="eightball.api_lnurl_pay",
)
async def api_lnurl_pay(
    request: Request,
    eightball_id: str,
):
    eightball = await get_eightball(eightball_id)
    if not eightball:
        return {"status": "ERROR", "reason": "No eightball found"}
    return {
        "callback": str(
            request.url_for(
                "eightball.api_lnurl_pay_callback", eightball_id=eightball_id
            )
        ),
        "maxSendable": eightball.lnurlpayamount * 1000,
        "minSendable": eightball.lnurlpayamount * 1000,
        "metadata": '[["text/plain", "' + eightball.name + '"]]',
        "tag": "payRequest",
    }


@eightball_ext.get(
    "/api/v1/lnurl/paycb/{eightball_id}",
    status_code=HTTPStatus.OK,
    name="eightball.api_lnurl_pay_callback",
)
async def api_lnurl_pay_cb(
    request: Request,
    eightball_id: str,
    amount: int = Query(...),
):
    eightball = await get_eightball(eightball_id)
    logger.debug(eightball)
    if not eightball:
        return {"status": "ERROR", "reason": "No eightball found"}

    payment_request = await create_invoice(
        wallet_id=eightball.wallet,
        amount=int(amount / 1000),
        memo=eightball.name,
        unhashed_description=f'[["text/plain", "{eightball.name}"]]'.encode(),
        extra={
            "tag": "EightBall",
            "eightballId": eightball_id,
            "extra": request.query_params.get("amount"),
        },
    )
    randomWord = random.choice(eightball.wordlist.split("\n"))
    return {
        "pr": payment_request,
        "routes": [],
        "successAction": {"tag": "message", "message": randomWord},
    }
