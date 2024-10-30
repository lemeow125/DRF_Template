from django.urls import path
from billing import views

urlpatterns = [
    path("", views.BillingHistoryView.as_view()),
]
