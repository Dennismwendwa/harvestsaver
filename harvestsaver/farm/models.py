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
    slug = models.SlugField()
    description = models.TextField()
    category = models.ForeignKey(EquipmentCategory,
                                 on_delete=models.SET_NULL, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              limit_choices_to={"is_equipment_owner": True})
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


class Review(models.Model):
    """This models stores reviews of products"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='reviews')
    review = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ("-pk",)

    def __str__(self):
        return f"{self.customer.username} {self.product.name}"

    @classmethod
    def all_product_review(cls, product):
        """Returns all reviews of a product"""
        return cls.objects.filter(product=product)


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
