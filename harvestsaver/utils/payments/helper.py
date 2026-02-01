
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.db.models import F

from farm.models import Cart, OrderItem
from transit.models import TransportBooking
from payment.models import Payment, Account
from utils.constants import PaymentMethod


def process_payment(order, user):
    from utils.constants import Status

    current_account = user.account.account_number
    cart_items = Cart.objects.filter(customer=user)
    transport = TransportBooking.objects.get(order=order)
    order_items = OrderItem.objects.filter(order=order)

    try:
        with transaction.atomic():
            if order.payment_method == PaymentMethod.WALLET:
                Payment.objects.create(
                    customer=user,
                    order=order,
                    payment_method=order.payment_method,
                    amount=order.total_amount
                )

                account = Account.objects.get(account_number=current_account)

                if account.account_balance < order.total_amount:
                    raise ValueError("Insufficient balance")

                account.account_balance = F("account_balance") - order.total_amount
                account.total_payment = F("total_payment") + order.total_amount
                account.last_transaction_date = timezone.now()
                account.save()

                order.status = Status.PAID
                order.save()

                cart_items.delete()

        return True, None

    except Exception as e:
        transport.delete()
        order_items.delete()
        return False, str(e)
