from typing import TYPE_CHECKING, Optional

from ..core.notification.utils import get_site_context
from ..core.notify_events import NotifyEventType
from ..core.utils import graphql_id

if TYPE_CHECKING:
    from ..account.models import User
    from ..app.models import App
    from ..plugins.manager import PluginsManager
    from .models import Invoice


def get_invoice_payload(invoice):
    return {
        "id": graphql_id(invoice),
        "number": invoice.number,
        "download_url": invoice.url,
        "order_id": graphql_id(invoice.order),
    }


def send_invoice(
    invoice: "Invoice",
    staff_user: "User",
    app: Optional["App"],
    manager: "PluginsManager",
):
    """Send an invoice to user of related order with URL to download it."""
    payload = {
        "invoice": get_invoice_payload(invoice),
        "recipient_email": invoice.order.get_customer_email(),  # type: ignore
        "requester_user_id": graphql_id(staff_user),
        "requester_app_id": graphql_id(app) if app else None,
        **get_site_context(),
    }

    channel_slug = None
    if invoice.order and invoice.order.channel:
        channel_slug = invoice.order.channel.slug
    manager.notify(
        NotifyEventType.INVOICE_READY, payload, channel_slug=channel_slug
    )  # type: ignore
    manager.invoice_sent(invoice, invoice.order.get_customer_email())  # type: ignore
