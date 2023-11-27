from rest_framework import serializers

from farm.models import Product, Equipment, Category
from accounts.models import User

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email",
                  "phone_number", "country"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    owner_details = OwnerSerializer(source="owner", read_only=True)
    category_details = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "quantity", "unit_of_measurement",
            "description", "image", "location", "harvest_date", "is_available",
            "owner", "category", "owner_details", "category_details"
        ]


class ProductDetailSerilizer(serializers.ModelSerializer):
    owner = OwnerSerializer(source="owner", read_only=True)
    category = CategorySerializer(source="category", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "price", "quantity", "unit_of_measurement",
            "description", "image", "location", "harvest_date", "is_available",
            "owner", "category"
        ]