from django.urls import path, include
from farm.urls import farm_urls

app_name = "farm"

urlpatterns = [
    path("", include("farm.urls.farm_urls")),
    path("admin/", include("farm.urls.admin_urls")),
]
