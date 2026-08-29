from django.urls import path

from accounts.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]
