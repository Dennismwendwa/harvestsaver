from django.contrib import admin
from .models import Account, Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order", "transaction_id", "amount", "timestamp"
    )

admin.site.register(Account)
admin.site.register(Payment, PaymentAdmin)

