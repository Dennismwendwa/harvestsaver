from django.contrib import admin
from .models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "quantity",
                    "unit_of_measurement", "location", "harvest_date",
                    "is_available",
                    )
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
