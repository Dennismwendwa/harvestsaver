from django.urls import path
from farm.views import admin


urlpatterns = [
    path("dashboard/", admin.admin_staff, name="admin_dashboard"),
    path("approve/<int:farm_id>/", admin.approve_farm, name="approve_farm"),
]
