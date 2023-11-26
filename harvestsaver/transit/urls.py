from django.urls import path
from .import views


app_name = "transit"

urlpatterns = [
    path("quote", views.transporthome, name="transportquote"),
    path("dashboard", views.all_transport, name="transporthome"),
    path("delivered/<int:pk>", views.delivered, name="delivered"),
    path("home", views.transportoptions, name="all_transport"),
]
