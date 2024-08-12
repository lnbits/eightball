from typing import Optional, Union

from lnbits.db import Database
from lnbits.helpers import insert_query, update_query

from .models import EightBall

db = Database("ext_eightball")


async def create_eightball(data: EightBall) -> EightBall:
    await db.execute(
        insert_query("eightball.maintable", data),
        (*data.dict().values(),),
    )
    return data


async def get_eightball(eightball_id: str) -> Optional[EightBall]:
    row = await db.fetchone(
        "SELECT * FROM eightball.maintable WHERE id = ?", (eightball_id,)
    )
    return EightBall(**row) if row else None


async def get_eightballs(wallet_ids: Union[str, list[str]]) -> list[EightBall]:
    if isinstance(wallet_ids, str):
        wallet_ids = [wallet_ids]

    q = ",".join(["?"] * len(wallet_ids))
    rows = await db.fetchall(
        f"SELECT * FROM eightball.maintable WHERE wallet IN ({q})", (*wallet_ids,)
    )
    return [EightBall(**row) for row in rows]


async def update_eightball(eightball: EightBall) -> EightBall:
    await db.execute(
        update_query("eightball.maintable", eightball),
        (*eightball.dict().values(),),
    )
    return eightball


async def delete_eightball(eightball_id: str) -> None:
    await db.execute("DELETE FROM eightball.maintable WHERE id = ?", (eightball_id,))
