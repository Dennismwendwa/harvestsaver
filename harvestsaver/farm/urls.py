from django.urls import path
from .import views


app_name = "farm"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<str:slug>", views.prodcuts_category,
         name="products_category"),
    path("product-detail/<str:slug>/<int:pk>", views.product_details,
         name="product_details"),
]
