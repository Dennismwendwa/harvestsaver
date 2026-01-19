from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator, MinValueValidator
from django.core.validators import MaxValueValidator, MaxValueValidator
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from farm.models import Order
from .validators import DimensionsValidator


class TransportBooking(models.Model):
    """
    This model stores all transport booking
    TRANSIT_OPTION: choices list for all options available
        Standard: This is the first option for transport
        Express: It offers faster delivaries
    STATUS: The status of the transport.
        Pending: for transport which have not started
        Transit: fro stransport which has not yet be delivered
        Delivered: for transport which is complete
    """
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
        ordering = ("-pk","-delivery_dateTime",) 

    def __str__(self):
        return f"{self.customer.username}'s Transport Booking"


class Quote(models.Model):
    """model for transport quotes inquire"""
    departure = models.CharField(max_length=100, verbose_name="Departure")
    delivery = models.CharField(max_length=100, verbose_name="Delivery")
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text="units kgs",
        verbose_name="Weight",
        validators=[
            MinValueValidator(
                limit_value=0.001, message="Weight must be at least 0.001 Kgs"
                ),
            MaxValueValidator(
                limit_value=1000000, message="Weight can not exceed 1,000,000 kgs"
            ),
        ]
        )
    dimensions = models.CharField(max_length=50, verbose_name="Demensions",
                                  validators=[DimensionsValidator()])
    name = models.CharField(max_length=50, verbose_name="Name")
    email = models.EmailField(verbose_name="Email",
                              validators=[EmailValidator(
                                message="Enter a valid email")])
    phone = models.CharField(max_length=50, verbose_name="Phone", validators=[
        RegexValidator(regex=r"^\+\d{1,}", message="Phone must start with a country code (+)"),
        MinLengthValidator(limit_value=13, message="Phone number is too short")
        ])
    message = models.TextField(verbose_name="Message")
    date = models.DateTimeField(auto_now_add=True, blank=True,)

    class meta:
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        ordering = ("-pk")

    def __str_(self):
        return f"Qoute from {self.name} email is {self.email}"
    

class VehicleCategory(models.Model):
    name = models.CharField(max_length=50, help_text="e.g Pickup, 3-Ton Truck")
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rate_per_km = models.DecimalField(max_digits=10, decimal_places=2)
    max_capacity_kg = models.IntegerField()

    class Meta:
        verbose_name = "Vehicle Category"
        verbose_name_plural = "Vehicle Categories"
        ordering = ("-pk",)

    def __str__(self):
        return self.name
    

class TerrainAdjustment(models.Model):
    ZONE_CHOICES = [
        ("tarmac", "Highway/Tarmac"),
        ("rural", "Rural/Muruam"),
        ("difficult", "Off-road/Muddy"),
    ]
    zone_type = models.CharField(max_length=20, choices=ZONE_CHOICES, unique=True)
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=100)

    class Meta:
        verbose_name = "Terrain Adjustment"
        verbose_name_plural = "Terrain Adjustments"
        ordering = ("-pk",)

    def __str__(self):
        return f"{self.zone_type} ({self.multiplier}x)"


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Molo Market")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ("-pk",)

    def __str__(self):
        return self.name

