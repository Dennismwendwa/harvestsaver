from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property

from utils.constants import UserRole, Country


class User(AbstractUser):
    gender = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=2, choices=Country.choices,
                               default=Country.KENYA)
    active_role = models.CharField(max_length=30,choices=UserRole.choices,
                                   default=UserRole.CUSTOMER)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} - {self.active_role}"
    
    @property
    def is_farmer(self):
        return self.active_role == UserRole.FARMER
    
    @property
    def is_equipment_owner(self):
        return self.active_role == UserRole.EQUIPMENT_OWNER
    
    @property
    def is_customer(self):
        return self.active_role == UserRole.CUSTOMER
    
    @property
    def is_system_staff(self):
        if self.is_staff:
            return True
        
        try:
            return self.staff_profile.role == "admin"
        except StaffProfile.DoesNotExist:
            return False
    
    @cached_property
    def staff_profile(self):
        if self.is_system_staff(self):
            return getattr(self, "staff_profile", None)
        return None
    
    @property
    def is_delivery(self):
        return self.staff_profile and self.staff_profile.role == "delivery"
    
    @property
    def is_admin(self):
        if self.is_superuser:
            return True
        
        try:
            return self.staff_profile.role == "admin"
        except StaffProfile.DoesNotExist:
            return False
    
    @property
    def is_warehouse(self):
        return self.staff_profile and self.staff_profile.role == "warehouse"


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
        abstract = True

class FarmerProfile(Profile):
    farm_name = models.CharField(max_length=100, blank=True, null=True)
    farm_size = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    crop_types = models.CharField(max_length=200, blank=True, null=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="farmer_profile"
    )

    class Meta:
        verbose_name = "Farmer Profile"
        verbose_name_plural = "Farmer Profiles"

    def __str__(self):
        return (
                f"Farmer name: {self.user.username} "
                f"Farm details: {self.farm_name}"
                )

class BuyerProfile(Profile):
    location = models.CharField(max_length=100, blank=True)
    preferred_categories = models.CharField(max_length=200, blank=True,
                                            null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="buyer_profile")

    class Meta:
        verbose_name = "Buyer Profile"
        verbose_name_plural = "Buyer Profiles"

    def __str__(self):
        return f"Buyer: ({self.pk}) {self.user.username} location: {self.location}"

class EquipmentOwnerProfile(Profile):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="equipment_owner_profile"
    )

    class Meta:
        verbose_name = "Equipment Owner Profile"
        verbose_name_plural = "Equipment Owner Profiles"

    def __str__(self):
        return f"Owner: {self.user.username}"
    
class StaffProfile(Profile):
    from farm.models import Hub
    ROLE_CHOICES = (
        ("delivery", "Delivery"),
        ("warehouse", "Warehouse"),
        ("admin", "Admin"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name="staff_profile")
    hub = models.ForeignKey(Hub, on_delete=models.PROTECT,
                            related_name="my_hub", null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = "Staff Profile"
        verbose_name_plural = "Staff Profiles"
        ordering = ("-pk",)

    def __str__(self):
        return f"User: ({self.user.username} - Role: {self.role})"

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
