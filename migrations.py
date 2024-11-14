async def m001_initial(db):
    """
    Initial templates table.
    """
    await db.execute(
        """
        CREATE TABLE eightball.maintable (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            name TEXT NOT NULL,
            wordlist TEXT NOT NULL,
            lnurlpayamount INTEGER DEFAULT 0,
            lnurlpay TEXT
        );
    """
    )


async def m002_drop_lnurlpay(db):
    """
    Migration to drop lnurlpay column from eightball.maintable.
    """
    # Drop lnurlpay from raisenow.raises
    await db.execute(
        """
        ALTER TABLE eightball.maintable
        DROP COLUMN lnurlpay;
        """
    )


async def m003_add_description(db):
    """
    Migration to add description column from eightball.maintable.
    """
    # Drop lnurlpay from raisenow.raises
    await db.execute(
        """
        ALTER TABLE eightball.maintable
        ADD COLUMN description TEXT;
        """
    )
