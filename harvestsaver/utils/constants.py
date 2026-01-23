from django.db import models

class UserRole(models.TextChoices):
    FARMER = "farmer", "Farmer"
    CUSTOMER = "customer", "Customer"
    EQUIPMENT_OWNER = "equipment_owner", "Equipment Owner" #equipment owner
    STAFF = "staff", "Staff"