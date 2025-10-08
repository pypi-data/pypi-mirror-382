from django.urls import path, include
from rest_framework.routers import DefaultRouter
from secure_bite.views import AuthenticationViewset

app_name = "secure_bite"

router = DefaultRouter()
router.register(r"auth", AuthenticationViewset, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
]
