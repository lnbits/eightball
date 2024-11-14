from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import (
    require_admin_key,
    require_invoice_key,
)
from lnbits.helpers import urlsafe_short_hash

from .crud import (
    create_eightball,
    delete_eightball,
    get_eightball,
    get_eightballs,
    update_eightball,
)
from .models import CreateEightBallData, EightBall

eightball_api_router = APIRouter()


@eightball_api_router.get("/api/v1/eightb", status_code=HTTPStatus.OK)
async def api_eightballs(
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(require_invoice_key),
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    eightballs = await get_eightballs(wallet_ids)
    return eightballs


@eightball_api_router.get(
    "/api/v1/eightb/{eightball_id}",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(require_invoice_key)],
)
async def api_eightball(eightball_id: str):
    eightball = await get_eightball(eightball_id)
    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    return eightball


@eightball_api_router.put("/api/v1/eightb/{eightball_id}")
async def api_eightball_update(
    data: CreateEightBallData,
    eightball_id: str,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    if not eightball_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall has no ID."
        )
    eightball = await get_eightball(eightball_id)
    assert eightball, "EightBall couldn't be retrieved"

    if wallet.wallet.id != eightball.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your EightBall."
        )
    for key, ball in data.dict().items():
        setattr(eightball, key, ball)
    eightball = await update_eightball(eightball)
    return eightball


@eightball_api_router.post(
    "/api/v1/eightb",
    status_code=HTTPStatus.CREATED,
)
async def api_eightball_create(
    data: CreateEightBallData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
) -> EightBall:
    if not data.wallet:
        data.wallet = wallet.wallet.id
    eightball = EightBall(
        id=urlsafe_short_hash(),
        **data.dict(),
    )
    return await create_eightball(eightball)


@eightball_api_router.delete("/api/v1/eightb/{eightball_id}")
async def api_eightball_delete(
    eightball_id: str, wallet: WalletTypeInfo = Depends(require_admin_key)
):
    eightball = await get_eightball(eightball_id)

    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )

    if eightball.wallet != wallet.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your EightBall."
        )

    await delete_eightball(eightball_id)
