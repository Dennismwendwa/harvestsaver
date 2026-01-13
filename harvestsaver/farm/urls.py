from django.urls import path
from .import views


app_name = "farm"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<str:slug>/", views.prodcuts_category,
         name="products_category"),
    path("product-detail/<str:slug>-<int:pk>/", views.product_details,
         name="product_details"),
    path("cart/add/<int:pk>", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart,
         name="remove_from_cart"),
    path("cart/", views.cart_items, name="cart_items"),
    path("cart/delete/<int:pk>/", views.delete_from_cart,
         name="delete_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/", views.succes_page, name="success_page"),
    path("equipment-category/<str:slug>/", views.equipment_category,
         name="equipment_category"),
    path("equipment-detail/<str:slug>/", views.equipment_detail,
         name="equipment_detail"),
    path("products/search", views.search, name="search"),
    path("all-products/", views.all_products, name="all_products"),
    path("all-equipments/", views.all_equipments, name="all_equipments"),
    path("farm/dashboard/", views.farmer_dashboard, name="farmer_dashboard"),
    path("equipment/dashboard/", views.equipment_dashboard,
         name="equipment_dashboard"),
    path("inquiry-for-<str:slug>/<int:pk>/", views.equipment_inquiry_respond,
         name="equipment_inquiry"),
]
