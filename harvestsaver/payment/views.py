from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db import transaction

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

from farm.models import Product, Order
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

def farm_payment_landing(request, pk):
    order = Order.objects.get(pk=pk)

    try:
        with transaction.Atomic():
            Payment.objects.create(
                customer=request.user,
                order=order,
                payment_method=order.payment_method,
                amount=order.total_amount
            )
        
        return redirect("payment:success")
    except Exception:
        return redirect("farm:checkout")


def create_checkoutfarmpayment(request, pk):
    order = Order.objects.get(pk=pk)
    account = request.user.account
    print(account)
    if request.method == "POST":
        try:
            with transaction.atomic():
                Payment.objects.create(
                customer=request.user,
                order=order,
                payment_method=order.payment_method,
                amount=order.total_amount
                )


            print("success")
            return redirect("payment:success")
        except Exception as e:
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
    def post(self, request, *args, **kwargs):

        success = reverse('payment:success')
        cancel = reverse('payment:cancel')

        product_id = self.kwargs["pk"]
        product = Order.objects.get(id=product_id)
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
                            #'images':["product.image.url",]
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": 2 #product.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + f"{success}",
            cancel_url=YOUR_DOMAIN + f"{cancel}",
        )
        
        return JsonResponse({
            'id': checkout_session.id
        })


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
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
            recipient_list=[customer_email],
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
            subject="Here is your product",
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
