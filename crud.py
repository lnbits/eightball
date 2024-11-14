from typing import List, Optional, Union

from lnbits.db import Database

from .models import EightBall

db = Database("ext_eightball")


async def create_eightball(data: EightBall) -> EightBall:
    await db.insert("eightball.maintable", data)
    return data


async def get_eightball(eightball_id: str) -> Optional[EightBall]:
    return await db.fetchone(
        "SELECT * FROM eightball.maintable WHERE id = :id",
        {"id": eightball_id},
        EightBall,
    )


async def get_eightballs(wallet_ids: Union[str, List[str]]) -> List[EightBall]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]
    q = ",".join([f"'{w}'" for w in wallet_ids])
    return await db.fetchall(
        f"SELECT * FROM eightball.maintable WHERE wallet IN ({q}) ORDER BY id",
        model=EightBall,
    )


async def update_eightball(eightball: EightBall) -> EightBall:
    await db.update("eightball.maintable", eightball)
    return eightball


async def delete_eightball(eightball_id: str) -> None:
    await db.execute(
        "DELETE FROM eightball.maintable WHERE id = :id", {"id": eightball_id}
    )
