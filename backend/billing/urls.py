from billing import views
from django.urls import path

urlpatterns = [
    path("", views.BillingHistoryView.as_view()),
]
