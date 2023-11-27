from django.urls import path
from . import views


app_name = "api"

urlpatterns = [
    path("products", views.ProductAPIView.as_view(), name="products_api"),
    path("products/<int:pk>", views.ProductDetailView.as_view(),
          name="product_detail_api"),
    path("products/search/", views.ProductSearchAPIView.as_view(),
          name="product_search_api"),
    path("equipments", views.equipment_list, name="equipments_api"),
    path("equipments/<int:pk>", views.equipment_detail,
          name="equipment_deatil_api"),
    path("equipments/search/", views.equipment_search,
          name="equipments_search_api"),
]
