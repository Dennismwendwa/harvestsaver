from django.urls import path
from . import views

app_name = "logistics"
urlpatterns = [
    # Deliary Dashboard
    path("delivery/", views.delivery_dashboard, name="delivarly"),
    path("prepare-dispatch/<int:booking_id>/", views.booking_dispach, name="prepare_dispatch"),
    path("mark-delivered/<int:booking_id>/", views.mark_received, name="mark_received"),
]