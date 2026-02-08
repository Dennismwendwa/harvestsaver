import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F, Sum, DecimalField, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import timedelta

from accounts.models import User, BuyerProfile
from .validators import validate_date_is_not_past
from utils.constants import UserRole, PaymentStatus, PaymentMethod, ItemStatus

class Hub(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.CharField()
    longitude = models.FloatField()
    location = models.ForeignKey(
        "logistics.Location",
        on_delete=models.PROTECT,
        related_name="hubs", null=True, blank=True
    )
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

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name}"

class ProductQuerySet(models.QuerySet):
    """
    Custom queryset for Product model providing domain-specific
    query helpers for analytics and reporting.
    """

    def for_farmer(self, farmer):
        """
        Filter products owned by a specific farmer.
        Args:
            farmer (User): The farmer (owner) whose products
                           should be returned.
        Returns:
            QuerySet: Products belonging to the given farmer.
        """
        return self.filter(farm__owner=farmer)
    
    def top_products(self, farmer, limit=5):
        """
        Return the top-selling products for a farmer based on
        total units sold.
        Each product in the returned queryset is annotated with:
            - units_sold: Total quantity sold across all orders.
            - revenue: Total revenue generated from the product.
        Only products belonging to the given farmer are considered.
        Args:
            farmer (User): The farmer (owner) whose products
                           should be analyzed.
            limit (int, optional): Maximum number of products
                                   to return. Defaults to 5.
        Returns:
            QuerySet: Annotated Product queryset ordered by
                      units_sold in descending order.
        """
        return (
            self.for_farmer(farmer)
            .annotate(
                units_sold=Coalesce(Sum("orderitem__quantity"), 0),
                revenue=Coalesce(
                    Sum(
                        F("orderitem__quantity") * F("price"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    ), Decimal("0.00"),
                )
            )
            .order_by("-units_sold")[:limit]
        )


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
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE,
                             null=True, blank=True,
                             related_name="products")
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, 
                            null=True, blank=True,
                            related_name="hub_products")
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField()
    category = models.ForeignKey(Category, null=True,
                                 on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit_weight_kg = models.DecimalField(max_digits=8, decimal_places=2,
                                        null=True, blank=True,
                                        help_text="Quantity per unit, e.g., 50 for a 50kg bag")
                                        # ALWAYS in kilograms regardless of unit type
    unit_quantity_type = models.CharField(max_length=10, null=True,blank=True,
                                          choices=UNIT_CHOICES,
                                          help_text="Unit type of the quantity"
    )
    description = models.TextField()
    image = models.ImageField(upload_to="products")
    harvest_date = models.DateField()
    is_available = models.BooleanField(default=True)
    is_perishable = models.BooleanField(default=False)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("-pk",)
    
    def __str__(self):
        return f"product: {self.name} farm: {self.farm.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def reduce_stock(self, qty):
        """Reduces stock after customer buys"""
        from django.db import transaction

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.pk)

            if product.quantity < qty:
                raise ValueError("Out of stock")
            
            product.quantity -= qty
            product.save(update_fields=["quantity"])

        
        

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete = models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PaymentStatus,
                              default=PaymentStatus.ACTIVE)
    is_checkout_active = models.BooleanField(default=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod)
    order_reference = models.CharField(
        max_length=50, unique=True, editable=False
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ("-order_date",)
        
        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=Q(status=PaymentStatus.ACTIVE),
                name="one_active_checkout_order_per_customer"
            )
        ]
        

    @staticmethod
    def generate_order_reference():
        year = timezone.now().year
        seq = Order.objects.filter(order_date__year=year).count() + 1
        return f"HARVEST-{year}-{seq:07d}"
    
    @property
    def is_completed(self):
        if self.status == PaymentStatus.COMPLETED:
            return True
        return False
    
    def save(self, *args, **kwargs):
        if not self.order_reference:
            self.order_reference = self.generate_order_reference()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.order_reference} - {self.customer.username}"


class OrderItem(models.Model):
    """This model stores the individual items within an order"""
    order = models.ForeignKey(Order, related_name="items",
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20,
                              choices=ItemStatus,
                              default=ItemStatus.PENDING)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ("-pk",)

    def __str__(self):
        return (
                f"Order: {self.order.order_reference} "
                f"Product: {self.product.name} Quantity: {self.quantity}"
                )
    
    @classmethod
    def total_sales_per_farmer(cls, farmer):
        """
        To return the total sales of the farmer including paid for items,
        pending payment items
        """
        total_sales = (
            OrderItem.objects
            .filter(product__farm__owner=farmer)
            .aggregate(
                total=Coalesce(
                    Sum(
                        F("quantity") * F("product__price"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    ),
                    Decimal("0.00")
                )
            )["total"]
        )
        return total_sales
    
    @classmethod
    def wallet_balance_for_farmer(cls, farmer):
        """
        To return the amount the farmer is to be paid. Only completed items
        and items not paid for before
        """
        from payment.models import PayoutItem
        paid_order_ids = PayoutItem.objects.values("order_item_id")

        available_balance = (
            cls.objects
            .filter(
                product__farm__owner=farmer,
                order__status=PaymentStatus.COMPLETED
            )
            .exclude(id__in=paid_order_ids)
            .aggregate(
                total=Coalesce(
                    Sum(F("quantity") * F("product__price")),
                    Decimal("0.00")
                )
            )
        )["total"]
        return available_balance

    @property
    def get_shipping_cost(self):
        shipping = (Decimal("0.09") * self.product.price * self.quantity)
        return  max(shipping.quantize(Decimal("0.01")), Decimal("300"))
    
    @classmethod
    def total_revenue(cls, farmer, start_date):
        qs = cls.objects.filter(
            product__farm__owner=farmer,
            order__status=PaymentStatus.COMPLETED
        )

        current = qs.filter(
            order__order_date__gte=start_date
        ).aggregate(
            total=Coalesce(
                Sum(F("quantity") * F("product__price")),
                Decimal("0.00")
            )
        )["total"]
        
        lifetime = qs.aggregate(
            total=Coalesce(
                Sum(F("quantity") * F("product__price")),
                Decimal("0.00")
            )
        )["total"]
        return {"current": current, "lifetime": lifetime}
    
    @classmethod
    def total_orders(cls, farmer, start_date):
        qs = cls.objects.filter(
            product__farm__owner=farmer,
            order__status=PaymentStatus.COMPLETED
        )

        current_orders_count = qs.filter(
            order__order_date__gte=start_date
        ).values("order_id").distinct().count()

        lifetime = qs.values("order_id").distinct().count()
        return {
            "current_orders_count": current_orders_count,
            "lifetime": lifetime
        }
    
    @classmethod
    def total_units(cls, farmer, start_time):
        """
        Returns total units sold, default to current month
        """
        qs = cls.objects.filter(
            product__farm__owner=farmer,
            order__status=PaymentStatus.COMPLETED
        )

        items = qs.filter(
            order__order_date__gte=start_time
        ).aggregate(
            total=Coalesce(Sum("quantity"), 0)
        )["total"]

        lifetime = qs.aggregate(
            total=Coalesce(Sum("quantity"), 0)
        )["total"]
        return {"current_items": items, "lifetime": lifetime}
    
    @classmethod
    def order_distribution(cls, farmer):
        qs = cls.objects.filter(
            product__farm__owner=farmer
        )

        completed = qs.filter(
            order__status=PaymentStatus.COMPLETED
        ).values("order_id").distinct().count()

        pending = qs.filter(
            order__status=PaymentStatus.PENDING
        ).values("order_id").distinct().count()

        cancelled = qs.filter(
            order__status=PaymentStatus.CANCELLED
        ).values("order_id").distinct().count()

        return {
            "completed": completed,
            "pending": pending,
            "cancelled": cancelled
        }

    @classmethod
    def sales_timeseries(cls, farmer, period="week"):
        """
        Calculates the Sales in week, month, or year.
        """
        today = timezone.now().date()

        if period == "week":
            start = today - timedelta(days=6)
            trunc = TruncDay
            step = "day"
            length = 7

        elif period == "month":
            start = today - timedelta(days=29)
            trunc = TruncDay
            step = "day"
            length = 30

        elif period == "year":
            start = today.replace(month=1, day=1)
            trunc = TruncMonth
            step = "month"
            length = 12
        else:
            raise ValueError("Invalid period")
        
        q1 = OrderItem.objects.filter(
                product__farm__owner=farmer,
                order__status=PaymentStatus.COMPLETED
            ).count()
        
        qs = (
            cls.objects.filter(
                product__farm__owner=farmer,
                order__status=PaymentStatus.COMPLETED,
                order__order_date__date__gte=start
            )
            .annotate(period=trunc("order__order_date"))
            .values("period")
            .annotate(
                total=Sum(
                    F("quantity") * F("product__price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .order_by("period")
        )
        data = {row["period"].date(): row["total"] for row in qs}

        result = []
        labels = []

        for i in range(length):
            if step == "day":
                point = start + timedelta(days=i)
                label = point.strftime("%d %b")
            else:
                point = today.replace(month=i+1, day=1)
                label = point.strftime("%b") # Jan Feb

            labels.append(label)
            result.append(float(data.get(point, Decimal("0.00"))))

        return {
            "labels": labels,
            "values": result
        }

    @property
    def total_weight(self):
        if not self.product.unit_weight_kg:
            return 0
        return self.quantity * self.product.unit_weight_kg


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
                              limit_choices_to={"role": UserRole.EQUIPMENT_OWNER})
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
