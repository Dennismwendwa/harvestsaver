from django.urls import path
from .views import ProductAPIView


app_name = "api"

urlpatterns = [
    path("product", ProductAPIView.as_view(), name="product_api"),
]
