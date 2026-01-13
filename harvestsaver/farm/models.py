import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import User


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
    owner = models.ForeignKey(User,
                              limit_choices_to={"role": User.Role.FARMER},
                              on_delete=models.CASCADE)
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
    location = models.CharField(max_length=100)
    harvest_date = models.DateField()
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-pk",)
    
    def __str__(self):
        return f"product: {self.name} Owner: {self.owner.username}"

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
    @property
    def calculate_total_cost(self):
        """This method calculates the total cost of item in cart
           cost per item times the number of such items in cart
        """
        if self.product and self.quantity:
            return self.product.price * self.quantity

        return 0.0


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
    """This model for equipments inquiry"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    customer = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()

    response = models.TextField(blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    admin_responded = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Equipment Inquiry"
        verbose_name_plural = "Equipments Inquiry"
        ordering = ("-pk",)
    def __str__(self):
        return (
                f"Inquiry by {self.customer} - {self.equipment.name}")


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
