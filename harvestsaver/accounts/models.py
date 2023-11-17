from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_staff = models.BooleanField("Is staff", default=False)
    is_farmer = models.BooleanField("Is farmer", default=False)
    is_equipment_owner = models.BooleanField("is_equipment_owner",
                                              default=False)
    is_customer = models.BooleanField("is_customer", default=False)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
