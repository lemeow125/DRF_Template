from django.urls import path, include
from notifications.views import NotificationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', NotificationViewSet,
                basename="Notifications")
urlpatterns = [
    path('', include(router.urls)),
]
