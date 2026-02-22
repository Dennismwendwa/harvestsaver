from django.db import transaction
from logistics.models import IssueRecord, TransferRecord
from farm.models import OrderItem
from utils.constants import BookStatus, ItemStatus


class DispatchService:

    @staticmethod
    @transaction.atomic
    def prepare_dispatch(*, user, booking, items):
        hub = user.staff_profile.hub

        for item, qty in items:
            if qty > item.remaining_quantity:
                raise ValueError("Over shipment detected")

            IssueRecord.objects.create(
                order_item=item,
                hub=hub,
                issued_by=user,
                quantity=qty
            )

            TransferRecord.objects.create(
                order_item=item,
                from_hub=hub,
                to_hub=booking.destination_hub,
                quantity_sent=qty
            )
            if item.remaining_quantity == 0:
                item.status = ItemStatus.IN_TRANSIT
            elif item.remaining_quantity > 0:
                item.status = ItemStatus.PARTIALLY_DISPATCHED
            item.save()

        DispatchService.update_booking_status(booking)

    @staticmethod
    def update_booking_status(booking):
        items = OrderItem.objects.filter(order=booking.order)

        total_remaining = sum(i.remaining_quantity for i in items)
        total_original = sum(i.quantity for i in items)

        if total_remaining == total_original:
            booking.status = BookStatus.PENDING

        elif total_remaining == 0:
            booking.status = BookStatus.IN_TRANSIT

        else:
            booking.status = BookStatus.PARTIALLY_DISPATCHED

        booking.save(update_fields=["status"])
