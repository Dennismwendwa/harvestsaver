from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UA
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Profile, FarmerProfile, BuyerProfile, EquipmentOwnerProfile

class UserAdmin(UA):
    list_display = ("username", "email", "role")

admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(BuyerProfile)
admin.site.register(FarmerProfile)
admin.site.register(EquipmentOwnerProfile)
