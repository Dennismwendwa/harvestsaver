from django.urls import path
from .import views


app_name = "farm"

urlpatterns = [
    path("", views.home, name="home"),
]
