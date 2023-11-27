from rest_framework import serializers
from farm.models import Product, Equipment


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
