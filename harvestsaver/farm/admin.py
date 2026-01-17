from django.contrib import admin
from .models import Category, Product, Cart, Order, OrderItem
from .models import (EquipmentCategory, Equipment, ProductReview,
                     FrequentQuestion, EquipmentReview, PlatformReview,
                     EquipmentInquiry, EquipmentRental)


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "quantity","unit_quantity",
                    "unit_quantity_type", "location", "harvest_date",
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

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "review", "rating",
                    "review_date", "product")

class PlatformReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "review", "rating",
                    "review_date", "category")

class EquipmentReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "review", "rating",
                    "review_date", "equipment")
    
class EquipmentRentalAdmin(admin.ModelAdmin):
    list_display = (
        "equipment", "renter", "start_date", "end_date", "total_cost",
        "created_at"
    )

class EquipmentInquiryAdmin(admin.ModelAdmin):
    list_display = (
        "equipment_name",
        "requester_name",
        "short_message",
        "requested_start_date",
        "requested_end_date",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
        "requested_start_date",
    )

    search_fields = (
        "equipment__name",
        "requester__username",
        "message",
    )

    readonly_fields = (
        "created_at",
        "responded_at",
    )

    fieldsets = (
        ("Inquiry Details", {
            "fields": (
                "equipment",
                "requester",
                "message",
            )
        }),
        ("Requested Period", {
            "fields": (
                "requested_start_date",
                "requested_end_date",
            )
        }),
        ("Response", {
            "fields": (
                "status",
                "response",
                "responded_at",
            )
        }),
        ("System Info", {
            "fields": (
                "created_at",
            )
        }),
    )

    ordering = ("-created_at",)

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    short_message.short_description = "Message"

    def equipment_name(self, obj):
        return obj.equipment.name

    equipment_name.short_description = "Equipment"

    def requester_name(self, obj):
        return obj.requester.get_full_name() or obj.requester.username

    requester_name.short_description = "Requester"
    

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(EquipmentCategory, EquipmentCategoryAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(FrequentQuestion)
admin.site.register(EquipmentInquiry, EquipmentInquiryAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(EquipmentReview, EquipmentReviewAdmin)
admin.site.register(PlatformReview, PlatformReviewAdmin)
admin.site.register(EquipmentRental, EquipmentRentalAdmin)
