from django.contrib import admin

from .models import TransportBooking, Quote

class TransportBookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "order",
                    "cost")


    def order_number(self, obj):
        return obj.order.order_reference if obj.order else "-"
    order_number.short_description = "Order"


admin.site.register(TransportBooking, TransportBookingAdmin)
admin.site.register(Quote)
