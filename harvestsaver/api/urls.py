from django.urls import path
from . import views


app_name = "api"

urlpatterns = [
    path("product", views.ProductAPIView.as_view(), name="product_api"),
    path("product/<int:pk>", views.ProductDetailView.as_view(),
          name="product_detail_api"),
]
