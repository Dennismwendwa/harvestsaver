from rest_framework import serializers

from farm.models import Product, Equipment, Category, EquipmentCategory
from farm.models import Review
from accounts.models import User


class OwnerSerializer(serializers.ModelSerializer):
    """Serializer for user model"""
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email",
                  "is_farmer", "phone_number", "country"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = "__all__"


class EquipmentCategorySerializer(serializers.ModelSerializer):
    """Serializer for Equipment Category model"""
    class Meta:
        model = EquipmentCategory
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    owner_details = OwnerSerializer(read_only=True)
    category_details = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "quantity", "unit_of_measurement",
            "description", "image", "location", "harvest_date", "is_available",
            "owner", "category", "owner_details", "category_details"
        ]


class ProductDetailSerilizer(serializers.ModelSerializer):
    """Serializer for Product model"""
    owner = OwnerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "quantity", "unit_of_measurement",
            "description", "image", "location", "harvest_date", "is_available",
            "owner", "category"
        ]


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model"""
    owner_details = OwnerSerializer(source="owner", read_only=True)
    category_details = EquipmentCategorySerializer(source="category", read_only=True)
    class Meta:
        model = Equipment
        fields = [
            "id", "name", "slug", "description", "location", "price_per_hour",
            "is_available", "image", "category", "owner", "owner_details",
            "category_details"
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    class Meta:
        model = Review
        fields = "__all__"


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
