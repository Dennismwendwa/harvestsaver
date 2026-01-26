from django.db import models

class UserRole(models.TextChoices):
    FARMER = "farmer", "Farmer"
    CUSTOMER = "customer", "Customer"
    EQUIPMENT_OWNER = "equipment_owner", "Equipment Owner" #equipment owner
    STAFF = "staff", "Staff"


class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED = "refunded", "Refunded"