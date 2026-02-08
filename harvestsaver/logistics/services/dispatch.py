from django.db import transaction
from logistics.models import IssueRecord, TransferRecord


class DispatchService:

    @staticmethod
    @transaction.atomic
    def prepare_dispatch(*, user, booking, items):
        hub = user.staff_profile.hub

        transfers = []

        for item in items:
            IssueRecord.objects.create(
                order_item=item,
                hub=hub,
                issued_by=user,
                quantity=item.quantity
            )

            transfer = TransferRecord.objects.create(
                order_item=item,
                from_hub=hub,
                to_hub=booking.destination_hub,
                quantity_sent=item.quantity
            )

            transfers.append(transfer)

        booking.status = "in_transit"
        booking.save()

        return transfers