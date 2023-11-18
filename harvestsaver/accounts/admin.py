from django.contrib import admin
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Profile, FarmerProfile, BuyerProfile, EquipmentOwnerProfile


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(BuyerProfile)
admin.site.register(FarmerProfile)
admin.site.register(EquipmentOwnerProfile)
