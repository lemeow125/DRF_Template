from django.urls import path
from payments import views


urlpatterns = [
    path("checkout_session/", views.StripeCheckoutView.as_view()),
    path("webhook/", views.stripe_webhook_view, name="Stripe Webhook"),
]
