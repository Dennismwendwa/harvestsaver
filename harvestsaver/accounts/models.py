from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_staff = models.BooleanField("Is staff", default=False)
    is_farmer = models.BooleanField("Is farmer", default=False)
    is_equipment_owner = models.BooleanField("is_equipment_owner",
                                              default=False)
    is_customer = models.BooleanField("is_customer", default=False)
    gender = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"username {self.username}"


class Profile(models.Model):
    """This is general profile for every user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="profile.png", upload_to="img")
    bio = models.TextField(blank=True, null=True)
    facebook_username = models.CharField(max_length=50, blank=True,
                                         null=True)
    instagram_username = models.CharField(max_length=50, blank=True,
                                          null=True)
    notification = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural ="Profiles"

    def __str__(self):
        return f"Profile of {self.user.username}"
