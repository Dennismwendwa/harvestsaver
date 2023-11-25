from django.urls import path
from .import views


app_name = "transit"

urlpatterns = [
    path("home", views.transporthome, name="transporthome"),
]
