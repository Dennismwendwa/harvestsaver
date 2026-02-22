from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import (FarmerProfile, BuyerProfile, EquipmentOwnerProfile,
                     StaffProfile)

class UserAdmin(UA):
    list_display = ("username", "email", "active_role")

    fieldsets = UA.fieldsets + (
        ("Custom Fields", {
            "fields": (
                "active_role",
                "gender",
                "phone_number",
                "country",
            ),
        }),
    )

    add_fieldsets = UA.add_fieldsets + (
        ("Custom Fields", {
            "fields": (
                "active_role",
                "gender",
                "phone_number",
                "country",
            ),
        }),
    )

class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "hub", "role")


admin.site.register(User, UserAdmin)
admin.site.register(BuyerProfile)
admin.site.register(FarmerProfile)
admin.site.register(EquipmentOwnerProfile)
admin.site.register(StaffProfile, StaffProfileAdmin)


