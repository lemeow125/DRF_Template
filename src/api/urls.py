from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

from core.settings import config

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    # Admin Panel
    path("admin/", admin.site.urls),
    # Swagger and Redoc API Doc URLs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Silk Enabled on DEBUG
    *([path("silk/", include("silk.urls", namespace="silk"))] if config.DEBUG else []),
]
