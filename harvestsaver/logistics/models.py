from django.db import models
from accounts.models import User
from farm.models import OrderItem, Farm, Hub

class TransferRecord(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    from_farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    to_hub = models.ForeignKey(Hub, on_delete=models.CASCADE)

    quantity_sent = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=8, decimal_places=2)

    received_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("in_transit", "In transit"),
            ("received", "Received"),
            ("rejected", "Rejected"),
        ],
        default="in_transit"
    )

    class Meta:
        verbose_name = "transfer record"
        verbose_name_plural = "transfer records"
        ordering = ("-received_at",)
        indexes = [
            models.Index(fields=["received_at"]),
        ]

    def __str__(self):
        return f"Item: {self.order_item.name} - {self.status}"


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
