from django.db import models
from accounts.models import User
from farm.models import OrderItem, Farm, Hub
from transit.models import TransportBooking, Carrier, VehicleCategory
from utils.constants import ItemStatus

class TransferRecordQuerySet(models.QuerySet):
    def inbound(self, hub):
        return self.filter(to_hub=hub)
    
    def outbound(self, hub):
        return self.filter(from_hub=hub)
    
    def in_transit(self):
        return self.filter(status=ItemStatus.IN_TRANSIT)
    
    def receivable(self, hub):
        return self.inbound(hub).in_transit()
    
    def dispatchable(self, hub):
        return self.outbound(hub).in_transit()
    
    def active(self):
        return self.exclude(status=ItemStatus.CANCELLED)

    def completed(self):
        return self.filter(status=ItemStatus.RECEIVED)
    
    def received_at_hub(self, hub):
        return self.filter(
            to_hub=hub,
            status=ItemStatus.RECEIVED
        )

class TransferRecord(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    from_hub = models.ForeignKey(Hub, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="outgoing_transfers")
    to_hub = models.ForeignKey(Hub, on_delete=models.CASCADE,
                               related_name="incoming_transfers")
    quantity_sent = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=8, decimal_places=2,
                                                null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.IN_TRANSIT
    )

    objects = TransferRecordQuerySet.as_manager()

    class Meta:
        verbose_name = "transfer record"
        verbose_name_plural = "transfer records"
        ordering = ("-sent_at",)
        indexes = [
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        try:
            return f"Item: {self.order_item} - {self.status}"
        except:
            return "TransferRecord (no order item yet)"
        

    def mark_received(self, qty):
        from django.utils import timezone
        if self.status != ItemStatus.IN_TRANSIT:
            raise ValueError("Cannot receive non-transit item")

        if qty > self.quantity_sent:
            raise ValueError("Received more than sent")

        self.quantity_received = qty
        self.received_at = timezone.now()

        if qty == self.quantity_sent:
            self.status = ItemStatus.RECEIVED
        else:
            self.status = ItemStatus.PARTIALLY_RECEIVED

        self.save()


class IssueRecordQuerySet(models.QuerySet):
    def for_hub(self, hub):
        """Return all issue records for the given hub."""
        return self.filter(hub=hub)
    
    def issued_by(self, user):
        """Return all issue records by the given user."""
        return self.filter(issued_by=user)

class IssueRecord(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE)
    issued_by = models.ForeignKey(User, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    issued_at = models.DateTimeField(auto_now_add=True)

    objects = IssueRecordQuerySet.as_manager()

    class Meta:
        verbose_name = "issue record"
        verbose_name_plural = "issue records"
        ordering = ("-issued_at",)
        indexes = [
            models.Index(fields=["issued_at", "issued_by"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order_item", "hub"],
                name="unique_issue_event"
            )
        ]

    def __str__(self):
        return (f"Item: {self.order_item.name} by ({self.issued_by.username})"
                f" at {self.issued_at}")


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            help_text="County names. e.g Nairobi")

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ("name",)

    def __str__(self):
        return self.name


class TransportAssignment(models.Model):
    booking = models.OneToOneField(
        TransportBooking,
        on_delete=models.CASCADE,
        related_name="assignment"
    )

    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT)
    vehicle = models.ForeignKey(VehicleCategory, on_delete=models.PROTECT)

    from_hub = models.ForeignKey(Hub, on_delete=models.PROTECT, related_name="dispatches")
    to_hub = models.ForeignKey(Hub, on_delete=models.PROTECT, related_name="receipts")

    status = models.CharField(
        max_length=20,
        choices=[
            ("loading", "Loading"),
            ("in_transit", "In Transit"),
            ("arrived", "Arrived"),
            ("closed", "Closed"),
        ],
        default="loading"
    )

    departed_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Transport Assignment"
        verbose_name_plural = "Transport Assignments"
        ordering = ("-departed_at",)

    def __str__(self):
        return f"Departed at: {self.departed_at}"

