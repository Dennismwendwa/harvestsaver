import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F, Sum, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

from accounts.models import User, BuyerProfile
from .validators import validate_file_is_pdf, validate_date_is_not_past

class Hub(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.CharField()
    longitude = models.FloatField()
    country = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    radius_km = models.IntegerField(default=30)

    class Meta:
        verbose_name = "Hub"
        verbose_name_plural = "Hubs"
        ordering = ("-pk",)

    def __str__(self):
        return self.name


class Farm(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              limit_choices_to={"role": "farmer"},
                              related_name="farms")
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.TextField()

    hub = models.ForeignKey(Hub, on_delete=models.PROTECT,
                            related_name="farms", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Farm"
        verbose_name_plural = "Farms"
        ordering = ("-created_at",)

    def __str__(self):
        if self.owner.first_name:
            return f"{self.name} ({self.owner.get_full_name})"
        return f"{self.name} ({self.owner})"


class Category(models.Model):
    """This is all products categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()

    class meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Model for all products availble in our site"""
    UNIT_CHOICES = [
        ("kg", "Kilogram"),           # grains, beans, vegetables
        ("g", "Gram"),                # small quantities for retail
        ("ton", "Tonne"),             # bulk harvests (maize, wheat, rice)
        ("l", "Liter"),               # milk, honey, juice
        ("ml", "Milliliter"),         # small liquid packaging
        ("pcs", "Pieces"),            # cabbage, pumpkin, watermelon
        ("bag", "Bag"),               # maize, rice, beans (50kg / 90kg)
        ("crate", "Crate"),           # tomatoes, oranges, mangoes
        ("bundle", "Bundle"),         # onions, spinach, herbs tied together
        ("dozen", "Dozen"),           # eggs, seedlings
        ("box", "Box"),               # sometimes fruits / seedlings
    ]
    farm = models.ForeignKey(Hub, on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name="products")
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    category = models.ForeignKey(Category, null=True,
                                 on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit_quantity = models.DecimalField(max_digits=8, decimal_places=2,
                                        null=True, blank=True,
                                        help_text="Quantity per unit, e.g., 50 for a 50kg bag"
    )
    unit_quantity_type = models.CharField(max_length=10, null=True,blank=True,
                                          choices=UNIT_CHOICES,
                                          help_text="Unit type of the quantity"
    )
    description = models.TextField()
    image = models.ImageField(upload_to="products")
    harvest_date = models.DateField()
    is_available = models.BooleanField(default=True)
    is_perishable = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-pk",)
    
    def __str__(self):
        return f"product: {self.name} farm: {self.farm.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        

class Cart(models.Model):
    """This models stores the products added to cart"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    added_on_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        ordering = ("-pk",)
        unique_together = ("product", "customer")

    def __str__(self):
        return (
                f"Customer: {self.customer.username} "
                f"product: {self.product.name} "
                f"Quantity: {self.quantity}"
                )
    
    @classmethod
    def total_cart_price(cls, user):
        cart_items = cls.objects.filter(customer=user)
        total = cart_items.aggregate(
            total=Coalesce(
                Sum(
                    F("quantity") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Decimal("0.00"),
            )
        )["total"]
        return total

class Order(models.Model):
    """This model stores the products add to cart"""
    customer = models.ForeignKey(User, on_delete = models.CASCADE)
    products = models.ManyToManyField(Product)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    class meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ("-pk",)

    def __str__(self):
        return (
                f"({self.pk}). Customer: {self.customer.username} "
                f"Order Id: {self.transaction_id} "
                f"Order amount: {self.total_amount}"
                )


def order_transaction_id():
    """This function generates unique transaction ID"""
    month = timezone.now().strftime("%B")[:4].upper()

    num = str(uuid.uuid4())[:10].upper()

    complete_id = f"{month}{num}"

    return complete_id


class OrderItem(models.Model):
    """This model stores the individual items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    class meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ("-pk",)

    def __str__(self):
        return (
                f"Order: {self.order.transaction_id} "
                f"Product: {self.product.name} Quantity: {self.quantity}"
                )

class EquipmentCategory(models.Model):
    """This model is for all equipment categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()

    class Meta:
        verbose_name = "Equipment Category"
        verbose_name_plural = "Equipment Categories"

    def __str__(self):
        return f"{self.name}"


class Equipment(models.Model):
    """This model store all current equitmwnr"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    category = models.ForeignKey(EquipmentCategory,
                                 on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              limit_choices_to={"role": User.Role.EQUIPMENT_OWNER})
    location = models.CharField(max_length=100)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to="equipment_img")

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipments"
        ordering = ("-pk",)
        unique_together = ("name", "owner")

    def __str__(self):
        return (
                f"Equipment: {self.name} "
                f"{self.location}"
                )

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class EquipmentInquiry(models.Model):
    """Inquiry before an equipment rental agreement"""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("responded", "Responded"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE, related_name="inquiries")
    requester = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="equipment_inquiries")
    message = models.TextField()
    requested_start_date = models.DateField(validators=[validate_date_is_not_past],
                                            null=True, blank=True)
    requested_end_date = models.DateField(validators=[validate_date_is_not_past],
                                          null=True, blank=True)
    response = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Equipment Inquiry"
        verbose_name_plural = "Equipment Inquiries"
        ordering = ("-created_at",)

    def __str__(self):
        return (
            f"Inquiry by {self.requester.username} "
            f"for {self.equipment.name}"
        )
    
    @property
    def is_responded_to(self):
        return self.status != "pending"

class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    review_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("-review_date",)

    def __str__(self):
        return f"Review by {self.customer}"
    
class ProductReview(Review):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "product"],
                name="unique_product_review"
            )
        ]

    def __str__(self):
        return f"{self.customer} → {self.product.name}"

class EquipmentReview(Review):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    class Meta:
        verbose_name = "Equipment Review"
        verbose_name_plural = "Equipment Reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "equipment"],
                name="unique_equipment_review"
            )
        ]

    def __str__(self):
        return f"{self.customer} → {self.equipment.name}"

class PlatformReview(Review):
    category = models.CharField(
        max_length=50,
        choices=[
            ("trust", "Trust"),
            ("usability", "Usability"),
            ("support", "Support"),
        ],
        default="trust",
    )

    class Meta:
        verbose_name = "Platform Review"
        verbose_name_plural = "Platform Reviews"

    def __str__(self):
        return f"{self.customer} → Platform"

class EquipmentRental(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="rentals"
    )
    renter = models.ForeignKey(
        BuyerProfile,
        on_delete=models.CASCADE,
        related_name="rentals"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Equipment Rental"
        verbose_name_plural = "Equipment Rentals"
        ordering = ("created_at",)


class FrequentQuestion(models.Model):
    """This models stores all Frequently asked Questions"""
    question = models.TextField()
    answer = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Frequent Question"
        verbose_name_plural = "Frequest Questions"
        unique_together = ("question", "answer")
        ordering = ("-pk",)
    
    def __str__(self):
        return f"{self.date}"
