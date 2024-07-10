import asyncio

from lnbits.core.models import Payment
from lnbits.core.services import websocket_updater
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener

from .crud import get_eightball


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())
    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") != "EightBall":
        return

    eightball_id = payment.extra.get("eightballId")
    eightball = await get_eightball(eightball_id)

    some_payment_data = {
        "name": eightball.name,
        "amount": payment.amount,
        "checking_id": payment.checking_id,
    }

    await websocket_updater(eightball_id, str(some_payment_data))
