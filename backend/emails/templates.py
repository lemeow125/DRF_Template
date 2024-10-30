from djoser import email
from django.utils import timezone


class ActivationEmail(email.ActivationEmail):
    template_name = "email_activation.html"


class PasswordResetEmail(email.PasswordResetEmail):
    template_name = "password_change.html"


class SubscriptionAvailedEmail(email.BaseEmailMessage):
    template_name = "subscription_availed.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = context.get("user")
        context["subscription_plan"] = context.get("subscription_plan")
        context["subscription"] = context.get("subscription")
        context["price_paid"] = context.get("price_paid")
        context["date"] = timezone.now().strftime("%B %d, %I:%M %p")
        context.update(self.context)
        return context


class SubscriptionRefundedEmail(email.BaseEmailMessage):
    template_name = "subscription_refunded.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = context.get("user")
        context["subscription_plan"] = context.get("subscription_plan")
        context["refund"] = context.get("refund")
        context["date"] = timezone.now().strftime("%B %d, %I:%M %p")
        context.update(self.context)
        return context


class SubscriptionCancelledEmail(email.BaseEmailMessage):
    template_name = "subscription_cancelled.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["user"] = context.get("user")
        context["subscription_plan"] = context.get("subscription_plan")
        context["date"] = timezone.now().strftime("%B %d, %I:%M %p")
        context.update(self.context)
        return context
