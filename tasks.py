import asyncio

from loguru import logger

from lnbits.core.models import Payment
from lnbits.core.services import create_invoice, websocket_updater
from lnbits.helpers import get_current_extension_name
from lnbits.tasks import register_invoice_listener

from .crud import get_eightball, update_eightball


#######################################
########## RUN YOUR TASKS HERE ########
#######################################

# The usual task is to listen to invoices related to this extension


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, get_current_extension_name())
    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


# Do somethhing when an invoice related top this extension is paid


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
