from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        FARMER = "farmer", "Farmer"
        CUSTOMER = "customer", "Customer"
        EQUIPMENT_OWNER = "equipment_owner", "Equipment Owner" #equipment owner
        STAFF = "staff", "Staff"

    role = models.CharField(max_length=30,choices=Role.choices,
                            default=Role.CUSTOMER)
    gender = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username}"
    
    @property
    def is_farmer(self):
        return self.role == self.Role.FARMER
    
    @property
    def is_equipment_owner(self):
        return self.role == self.Role.EQUIPMENT_OWNER
    
    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER


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


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farm_name = models.CharField(max_length=100, blank=True, null=True)
    farm_size = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    crop_types = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"

    def __str__(self):
        return (
                f"Farmer name: {self.user.username} "
                f"Farm details: {self.farm_name}"
                )

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True)
    preferred_categories = models.CharField(max_length=200, blank=True,
                                            null=True)
    purchase_hostory = models.TextField(blank=True, null=True)
    payment_info = models.CharField(max_length=100, blank=True, null=True)

    class meta:
        verbose_name = "Buyer Profile"
        verbose_name_plural = "Buyer Profiles"

    def __str__(self):
        return f"Buyer: {self.user.username} location: {self.location}"


class EquipmentOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rental_history = models.CharField(max_length=300, blank=True, null=True)

    class meta:
        verbose_name = "Equipment Owner Profile"
        verbose_name_plural = "Equipment Owner Profiles"

    def __str__(self):
        return f"Owner: {self.user.username}"


class Contact(models.Model):
    """
    This model stores all contact information
    Args: name - required
          email - required
          subject - required
          message - required
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.TextField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ("-pk",)

    def __str__(self):
        return f"Contact by {self.name} Email: {self.email}"
