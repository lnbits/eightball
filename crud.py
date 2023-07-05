from typing import List, Optional

from lnbits.db import SQLITE
from . import db
from .wordlists import phrases
from .models import Game
from lnbits.helpers import urlsafe_short_hash


async def add_game(
    name: str,
    description: str,
    user: str,
    wallet: str,
    price: int,
    wordlist: str,
) -> int:
    game_id = urlsafe_short_hash()
    await db.execute(
        """
        INSERT INTO eightball.games (id, name, description, user, wallet, price, wordlist)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (game_id, name, description, user, wallet, price, wordlist),
    )
    return await get_games(user)


async def get_game(id: str) -> Optional[Game]:
    row = await db.fetchone("SELECT * FROM eightball.games WHERE id", (id,))
    return Game(**dict(row)) if row else None


async def get_games(user: str) -> List[Game]:
    rows = await db.fetchall("SELECT * FROM eightball.games WHERE user = ?", (user,))
    return [Game(**dict(row)) for row in rows]


async def delete_game(game_id: str):
    result = await db.execute(
        """
        DELETE FROM eightball.games WHERE id = ?
        """,
        (game_id),
    )
    game = await get_game(game_id)
    return await get_games(game.user)
