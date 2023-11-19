from django.db import models
from django.utils import timezone
import uuid

from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()

    class meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    owner = models.ForeignKey(User,
                              limit_choices_to={"is_farmer": True},
                              on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    category = models.ForeignKey(Category, null=True,
                                 on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit_of_measurement = models.CharField(max_length=20)
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
                f"Customer: {self.customer.username} "
                f"Order Id: {self.transaction_id} "
                f"Order amount: {self.total_amount}"
                )


def order_transaction_id():
    month = timezone.now().strftime("%B")[:4].upper()

    num = str(uuid.uuid4())[:10].upper()

    complete_id = f"{month}{num}"

    return complete_id

























