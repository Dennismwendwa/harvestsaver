from django.urls import path
from .import views


app_name = "transit"

urlpatterns = [
    path("quote", views.transporthome, name="transportquote"),
    path("home", views.all_transport, name="transporthome"),
    path("delivered/<int:pk>", views.delivered, name="delivered"),
]
