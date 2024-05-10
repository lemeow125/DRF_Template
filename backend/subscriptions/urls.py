from django.urls import path, include
from subscriptions import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'plans', views.SubscriptionPlanViewset,
                basename="Subscription Plans")
router.register(r'self', views.UserSubscriptionViewset,
                basename="Self Subscriptions")
router.register(r'user_group', views.UserGroupSubscriptionViewet,
                basename="Group Subscriptions")
urlpatterns = [
    path('', include(router.urls)),
]
