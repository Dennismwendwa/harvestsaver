from django.contrib import admin
from .models import IssueRecord, TransferRecord, Location

class TransferRecordAdmin(admin.ModelAdmin):
    list_display = ("order_item", "from_hub", "to_hub", "status", "quantity_sent",
                    "quantity_received", "received_at",)
    

class IssuedRecordAdmin(admin.ModelAdmin):
    list_display = ("order_item", "issued_by", "quantity", "issued_at")

class LocationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

admin.site.register(IssueRecord, IssuedRecordAdmin)
admin.site.register(TransferRecord, TransferRecordAdmin)
admin.site.register(Location, LocationAdmin)

