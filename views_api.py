from http import HTTPStatus
from fastapi import Depends, Query, Request
from starlette.exceptions import HTTPException
from lnbits.core.crud import get_user
from lnbits.decorators import (
    WalletTypeInfo,
    get_key_type,
    require_admin_key,
)

from . import eightball_ext
from .crud import (
    create_eightball,
    update_eightball,
    delete_eightball,
    get_eightball,
    get_eightballs,
)
from .models import CreateEightBallData


@eightball_ext.get("/api/v1/eightb", status_code=HTTPStatus.OK)
async def api_eightballs(
    req: Request,
    all_wallets: bool = Query(False),
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    wallet_ids = [wallet.wallet.id]
    if all_wallets:
        user = await get_user(wallet.wallet.user)
        wallet_ids = user.wallet_ids if user else []
    return [eightball.dict() for eightball in await get_eightballs(wallet_ids, req)]


@eightball_ext.get("/api/v1/eightb/{eightball_id}", status_code=HTTPStatus.OK)
async def api_eightball(
    req: Request, eightball_id: str, WalletTypeInfo=Depends(get_key_type)
):
    eightball = await get_eightball(eightball_id, req)
    if not eightball:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    return eightball.dict()


@eightball_ext.put("/api/v1/eightb/{eightball_id}")
async def api_eightball_update(
    req: Request,
    data: CreateEightBallData,
    eightball_id: str,
    wallet: WalletTypeInfo = Depends(get_key_type),
):
    if not eightball_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="EightBall does not exist."
        )
    eightball = await get_eightball(eightball_id, req)
    assert eightball, "EightBall couldn't be retrieved"

    if wallet.wallet.id != eightball.wallet:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not your EightBall."
        )
    eightball = await update_eightball(
        eightball_id=eightball_id, **data.dict(), req=req
    )
    return eightball.dict()


@eightball_ext.post("/api/v1/eightb", status_code=HTTPStatus.CREATED)
async def api_eightball_create(
    req: Request,
    data: CreateEightBallData,
    wallet: WalletTypeInfo = Depends(require_admin_key),
):
    eightball = await create_eightball(wallet_id=wallet.wallet.id, data=data, req=req)
    return eightball.dict()


@eightball_ext.delete("/api/v1/eightb/{eightball_id}")
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
    return "", HTTPStatus.NO_CONTENT
