from django.contrib import admin
from .models import Category, Product, Cart, Order, OrderItem
from .models import EquipmentCategory, Equipment, Review, FrequentQuestion
from .models import EquipmentInquiry


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "quantity",
                    "unit_of_measurement", "location", "harvest_date",
                    "is_available",
                    )
    prepopulated_fields = {"slug": ("name",)}

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "customer", "order_date", "status", "total_amount",
        "shipping_address", "transaction_id", "payment_method"
    )

class EquipmentCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class EquipmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(EquipmentCategory, EquipmentCategoryAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Review)
admin.site.register(FrequentQuestion)
admin.site.register(EquipmentInquiry)
