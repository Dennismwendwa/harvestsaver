import random
import uuid

from django.db import models
from accounts.models import User
from farm.models import Order


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