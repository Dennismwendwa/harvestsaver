from django.contrib import admin

from .models import TransportBooking, Quote, VehicleCategory, Carrier

class TransportBookingAdmin(admin.ModelAdmin):
    list_display = ("order_number",
                    "transport_option", "source_hub",
                    "destination_hub",  "status", "created_at",
                     "requested_pickup_at", "cost",)


    def order_number(self, obj):
        return obj.order.order_reference if obj.order else "-"
    order_number.short_description = "Order"

class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "base_fee", "rate_per_km", "max_capacity_kg")
    search_fields = ("max_capacity_kg",)


class CarrierAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "name", "contact", "created_at")


admin.site.register(TransportBooking, TransportBookingAdmin)
admin.site.register(Quote)
admin.site.register(VehicleCategory, VehicleCategoryAdmin)
admin.site.register(Carrier, CarrierAdmin)
