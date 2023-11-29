import random
import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.db import models, transaction

from farm.models import order_transaction_id
from accounts.models import User
from farm.models import Order, Cart, OrderItem
from transit.models import TransportBooking


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=200, unique=True)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2,
                                          default=1000000)
    opening_date = models.DateTimeField(auto_now_add=True)

    last_transaction_date = models.DateTimeField(null=True)
    total_withdraw = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_deposit = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_transfar = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_paybil = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    total_trans_amount = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "Accounts"
        ordering = ("-pk",)

    def __str__(self):
        return f"{self.user.username} {self.account_number}"


def accounts_number(user_id):
     
	string_part = "ACC"
	randd = random.randint(1, 10)
	
	uuid_part = str(uuid.uuid4().hex[:8])
	user_num = str(int(user_id) - sum(ord(char) for char in str(user_id))).replace("-", "")
	user_num = int(user_num)
	user_num = str(user_num - randd)

	bank_account_number = string_part + uuid_part + user_num

	ciphertext = bank_account_number.upper()

	return ciphertext

class Payment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
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


def order_payment(shipping_address,payment_method, transport, pickup_location, request):

    cart_items = Cart.objects.filter(customer=request.user).all()
    products_instances = [cart_item.product for cart_item in cart_items]
    
    if cart_items:
        total = 0
        for item in cart_items:
            subtotal = item.calculate_total_cost
            total += subtotal
        
    shipping = round((Decimal(3 / 100) * total), 2)
    total_cost = (total + shipping)

    transaction_id=order_transaction_id()
    order = Order.objects.create(customer=request.user,
                            total_amount=total_cost,
                            transaction_id=transaction_id,
                            shipping_address=shipping_address,
                            payment_method=payment_method,
                            status="payed",
                            )
    order.products.set(products_instances)
        
    for cart_item in cart_items:
        OrderItem.objects.create(order=order,
                                     product=cart_item.product,
                                     quantity=cart_item.quantity)

    cart_items.delete()

    today = timezone.now()
    pickup_date_time = today + timedelta(days=4)
        
    try:
        TransportBooking.objects.create(
            customer=request.user,
            order=order,
            pickup_location=pickup_location,
            transport_option=transport,
            cost=shipping,
            pickup_date_time=pickup_date_time,
            )
    except Exception as e:
        print(e)
        return "payment_error", None
    
    return "payment_seccess", order.pk