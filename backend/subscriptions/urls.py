from django.urls import include, path
from rest_framework.routers import DefaultRouter
from subscriptions import views

router = DefaultRouter()
router.register(r"plans", views.SubscriptionPlanViewset, basename="Subscription Plans")
router.register(r"self", views.UserSubscriptionViewset, basename="Self Subscriptions")
router.register(
    r"user_group", views.UserGroupSubscriptionViewet, basename="Group Subscriptions"
)
urlpatterns = [
    path("", include(router.urls)),
]
