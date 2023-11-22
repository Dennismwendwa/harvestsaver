from django.db import models
from django.utils import timezone

from accounts.models import User
from farm.models import Order


class TransportBooking(models.Model):
    """This model stores all transport booking"""
    TRANSIT_OPTIONS = [
        ("Standard Delivery", "Standard Delivery"),
        ("Express Delivery", "Express Delivery"),
    ]
    STATUS = [
        ("Pending", "Pending"),
        ("Transit", "Transit"),
        ("Delivered", "Delivered"),
    ]
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    pickup_location = models.CharField(max_length=200)
    transport_option = models.CharField(max_length=100, choices=TRANSIT_OPTIONS)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_date_time = models.DateTimeField()
    delivery_dateTime = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending", choices=STATUS)

    class Meta:
        verbose_name = "Transport Booking"
        verbose_name_plural = "Transport Bookings"
        unique_together = ("customer", "order",)
        ordering = ("-pk",)

    def __str__(self):
        return f"{self.customer.username}'s Transport Booking"
