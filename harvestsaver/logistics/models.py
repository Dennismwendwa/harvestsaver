from django.db import models
from accounts.models import User
from farm.models import OrderItem, Farm, Hub
from transit.models import TransportBooking, Carrier, VehicleCategory

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
        choices=[
            ("in_transit", "In transit"),
            ("received", "Received"),
            ("rejected", "Rejected"),
            ("damaged", "Damaged"),
        ],
        default="in_transit"
    )

    class Meta:
        verbose_name = "transfer record"
        verbose_name_plural = "transfer records"
        ordering = ("-sent_at",)
        indexes = [
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        try:
            return f"Item: {self.order_item.name} - {self.status}"
        except:
            return "TransferRecord (no order item yet)"

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
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    hub = models.ManyToManyField(Hub, related_name="my_location")

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ("-pk",)

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

