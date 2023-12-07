from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.db.models import F

from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

import json
import stripe
import logging

logger = logging.getLogger(__name__)

from farm.models import Product, Order, Cart, OrderItem
from transit.models import TransportBooking
from .models import Payment, Account

stripe.api_key = settings.STRIPE_SECRET_KEY

def farm_payment_landing(request, pk):
    order = Order.objects.get(pk=pk)
    pass

def create_checkoutfarmpayment(request, pk):
    """This function processes payment in farm pay service"""
    order = Order.objects.get(pk=pk)
    current_account = request.user.account.account_number
    cart_items = Cart.objects.filter(customer=request.user).all()
    transport = TransportBooking.objects.get(order=order)
    order_items = OrderItem.objects.filter(order=order).all()
    
    if request.method == "POST":
        try:
            with transaction.atomic():
    
                Payment.objects.create(
                customer=request.user,
                order=order,
                payment_method=order.payment_method,
                amount=order.total_amount
                )
                
                account = Account.objects.get(account_number=current_account)

                if account.account_balance >= order.total_amount:
                    account.account_balance = F("account_balance") - order.total_amount
                    account.total_payment = F("total_payment") + order.total_amount
                    account.last_transaction_date = timezone.now()
                    account.save()
                    account.refresh_from_db()
                
                order.status = "payed"
                order.save()
                cart_items.delete()

            return redirect("payment:success")
        except Exception as e:
            transport.delete()
            order_items.delete()
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect("payment:payment_failed")
    return render(request, "payment/farmpayment.html")
        

@login_required
def service_payment(request, pk):
    product_type = "service"
    product = Order.objects.get(pk=pk)
    context = {
            "product": product,
            "product_type": product_type,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            }

    return render(request, "payment/landing.html", context)
        
class SuccessView(TemplateView):
    template_name = "payment/success.html"


class CancelView(TemplateView):
    template_name = "payment/cancel.html"


# @method_decorator(csrf_exempt, name='dispatch')
class CreateCheckoutSessionView(View):
    """This is strip payment view. For processing customer payments"""
    def post(self, request, *args, **kwargs):

        success = reverse('payment:success')
        cancel = reverse('payment:cancel')

        product_id = self.kwargs["pk"]
        product = Order.objects.get(id=product_id)
        cart_items = Cart.objects.filter(customer=request.user).all()
        transport = TransportBooking.objects.get(order=product)
        YOUR_DOMAIN = settings.YOUR_DOMAIN
        payment_method_types="card"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(product.total_amount * 100),
                        'product_data': {
                            'name': product.transaction_id,
                            'images':["product.image.url",]
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + f"{success}",
            cancel_url=YOUR_DOMAIN + f"{cancel}",
        )
        
        product.status = "payed"
        product.save()
        cart_items.delete()

        return JsonResponse({
            'id': checkout_session.id
        })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    logger.info("\n\nWebhook payload: %s\n\n", payload)
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logger.error("ValueError while processing webhook: %s", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error("SignatureVerificationError while processing webhook: %s", e)
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"""
            Thanks for your purchase. Here is the product you ordered.
            The URL is {product.url}
            """,
            recipient_list = ["dennissoftware3@gmail.com",],
            from_email="dennismusembi2@gmail.com"
        )

        # TODO - decide whether you want to send the file or the URL

    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your Order",
            message=f"""
            Thanks for your purchase. Here is the product you ordered.
            The URL is {product.url}
            """,
            recipient_list=[customer_email],
            from_email="dennismusembi2@gmail.com"
        )

    return HttpResponse(status=200)


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            product_id = self.kwargs["pk"]

            product = Product.objects.get(id=product_id)
            intent = stripe.PaymentIntent.create(
                amount=int(product.price * 100),
                currency='usd',
                customer=customer['id'],
                metadata={
                    "product_id": product.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})
