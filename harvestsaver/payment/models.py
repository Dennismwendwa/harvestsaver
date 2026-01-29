import random
import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce

from accounts.models import User
from farm.models import Order, Cart, OrderItem
from transit.models import TransportBooking
from utils.constants import PaymentStatus, Country


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=200, unique=True)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2,
                                          default=0)
    opening_date = models.DateTimeField(auto_now_add=True)

    last_transaction_date = models.DateTimeField(null=True)
    total_payment = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_deposit = models.DecimalField(max_digits=12, decimal_places=4, default=0)
  

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ("-pk",)

    @staticmethod
    def generate_account_number(country_code: str) -> str:
        """
        Returns a unique, hard-to-guess account number.
        Format: <COUNTRY>-<RANDOM4><SEQUENTIAL6>
        Example: KE-A7F312-000123
        """
        from utils.constants import COUNTRY_NUMERIC, APP_CODE, PRODUCT_CODE
        country_num = COUNTRY_NUMERIC.get(country_code, "000")
        prefix = f"{country_num}{APP_CODE}{PRODUCT_CODE}"

        last = Account.objects.filter(
            account_number__startswith=prefix
        ).order_by("-account_number").first()

        if not last:
            next_seq = 1
        else:
            last_seq = int(last.account_number[-10:])
            next_seq = last_seq + 1

        return f"{prefix}{next_seq:010d}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number(self.user.country)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} {self.account_number}"




class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True,)
    provider = models.CharField(max_length=50)  # mpesa, stripe, wallet
    status = models.CharField(max_length=20, choices=PaymentStatus,
                              )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
         verbose_name = "Payment"
         verbose_name_plural = "Payments"
         ordering = ("-pk",)

    def __str__(self):
         return f"{self.customer.username} {self.order}"
    

def customer_id():
    num = str(uuid.uuid4())
    return num


class CustomerSession(models.Model):
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    date = models.DateTimeField()

    order_id = models
    current = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=100, decimal_places=2)

    class Meta:
        verbose_name = "Customer Session"
        verbose_name_plural = "Customer Sessions"
        ordering = ("-pk",)


@transaction.atomic
def process_order(shipping_address, payment_method, transport, delivery_destination, request):
    from utils.constants import PaymentStatus

    user = request.user
    cart_items = Cart.objects.filter(customer=user)

    if not cart_items.exists():
        return None

    total = Cart.total_cart_price(user)
    shipping = round(Decimal("0.09") * total, 2)
    total_cost = total + shipping

    order = Order.objects.filter(
        customer=user,
        status=PaymentStatus.PENDING,
        is_checkout_active=True
    ).first()

    if not order:
        order = Order.objects.create(
            customer=user,
            status=PaymentStatus.PENDING,
            is_checkout_active=True,
            total_amount=total_cost,
            shipping_address=shipping_address,
            payment_method=payment_method,
        )
    else:
        # Update totals if cart changed
        order.total_amount = total_cost
        order.shipping_address = shipping_address
        order.payment_method = payment_method
        order.save()

        # Clean previous checkout attempt
        order.orderitem_set.all().delete()

    today = timezone.now()

    for cart_item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity
        )

        pickup_date_time = (
            today + timedelta(days=1)
            if order_item.product.is_perishable
            else today + timedelta(days=4)
        )

        TransportBooking.objects.create(
            customer=user,
            order_item=order_item,
            pickup_location=order_item.product.farm.hub.name,
            destination=delivery_destination,
            transport_option=transport,
            cost=order_item.get_shipping_cost,
            pickup_date_time=pickup_date_time,
        )

    return order


class Payout(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Payout amount {self.amount} to {self.farmer.username}"
    
    @classmethod
    def total_paid(cls, farmer):
        total_paid = (
            Payout.objects
            .filter(farmer=farmer)
            .aggregate(
                total=Coalesce(Sum("amount"), Decimal("0.00"))
                )
        )["total"]
        return total_paid

class PayoutItem(models.Model):
    payout = models.ForeignKey(Payout, related_name="items", on_delete=models.CASCADE)
    order_item = models.OneToOneField(OrderItem, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "PayoutItem"
        verbose_name_plural = "PayoutItems"
        ordering = ("-pk",)
    
    def __str__(self):
        return f"{self.payout} - {self.order_item}"
