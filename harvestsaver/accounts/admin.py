from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import FarmerProfile, BuyerProfile, EquipmentOwnerProfile

class UserAdmin(UA):
    list_display = ("username", "email", "role")

    fieldsets = UA.fieldsets + (
        ("Custom Fields", {
            "fields": (
                "role",
                "gender",
                "phone_number",
                "country",
            ),
        }),
    )

    add_fieldsets = UA.add_fieldsets + (
        ("Custom Fields", {
            "fields": (
                "role",
                "gender",
                "phone_number",
                "country",
            ),
        }),
    )

admin.site.register(User, UserAdmin)
admin.site.register(BuyerProfile)
admin.site.register(FarmerProfile)
admin.site.register(EquipmentOwnerProfile)


