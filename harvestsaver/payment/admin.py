from django.contrib import admin
from .models import Account, Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "customer", "order", "amount", "timestamp", "payment_method"
    )

admin.site.register(Account)
admin.site.register(Payment, PaymentAdmin)

