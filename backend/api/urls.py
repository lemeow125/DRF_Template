from config.settings import DEBUG, MEDIA_ROOT, SERVE_MEDIA
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("subscriptions/", include("subscriptions.urls")),
    path("notifications/", include("notifications.urls")),
    path("billing/", include("billing.urls")),
    path("stripe/", include("payments.urls")),
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# URLs for local development
if DEBUG and SERVE_MEDIA:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static("media/", document_root=MEDIA_ROOT)
if DEBUG:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
