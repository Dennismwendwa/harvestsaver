from django.urls import path
from .import views


app_name = "farm"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<str:slug>", views.prodcuts_category,
         name="products_category"),
    path("product-detail/<str:slug>/<int:pk>", views.product_details,
         name="product_details"),
    path("cart/add/<int:pk>", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>", views.remove_from_cart,
         name="remove_from_cart"),
    path("cart", views.cart_items, name="cart_items"),
    path("cart/delete/<int:pk>", views.delete_from_cart,
         name="delete_from_cart"),
]
