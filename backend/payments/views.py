from config.settings import (
    STRIPE_SECRET_KEY,
    STRIPE_SECRET_WEBHOOK,
    URL_SCHEME,
    FRONTEND_ADDRESS,
    FRONTEND_PORT,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import logging
import stripe
from subscriptions.models import SubscriptionPlan, UserSubscription
from accounts.models import CustomUser
from rest_framework.decorators import api_view
from subscriptions.tasks import get_user_subscription
import json
from emails.templates import (
    SubscriptionAvailedEmail,
    SubscriptionRefundedEmail,
    SubscriptionCancelledEmail,
)
from django.core.cache import cache
from payments.serializers import CheckoutSerializer
from drf_spectacular.utils import extend_schema

stripe.api_key = STRIPE_SECRET_KEY


@extend_schema(request=CheckoutSerializer)
class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get subscription ID from POST
            USER = CustomUser.objects.get(id=self.request.user.id)
            data = json.loads(request.body)
            subscription_id = data.get("subscription_id")
            annual = data.get("annual")

            # Validation for subscription_id field
            try:
                subscription_id = int(subscription_id)
            except:
                return Response(
                    {"error": "Invalid value specified in subscription_id field"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Validation for annual field
            try:
                annual = bool(annual)
            except:
                return Response(
                    {"error": "Invalid value specified in annual field"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Return an error if the user already has an active subscription
            EXISTING_SUBSCRIPTION = get_user_subscription(USER.id)
            if EXISTING_SUBSCRIPTION:
                return Response(
                    {
                        "error": f"User is already subscribed to: {EXISTING_SUBSCRIPTION.subscription.name}"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Attempt to query the subscription
            SUBSCRIPTION = SubscriptionPlan.objects.filter(id=subscription_id).first()

            # Return an error if the plan does not exist
            if not SUBSCRIPTION:
                return Response(
                    {"error": "Subscription plan not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get the stripe_price_id from the related StripePrice instances
            if annual:
                PRICE = SUBSCRIPTION.annual_price
            else:
                PRICE = SUBSCRIPTION.monthly_price

            # Return 404 if no price is set
            if not PRICE:
                return Response(
                    {"error": "Specified price does not exist for plan"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            PRICE_ID = PRICE.stripe_price_id
            prorated = PRICE.prorated

            # Return an error if a user is in a user_group and is availing pro-rated plans
            if not USER.user_group and SUBSCRIPTION.group_exclusive:
                return Response(
                    {"error": "Regular users cannot avail prorated plans"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            success_url = (
                f"{URL_SCHEME}://{FRONTEND_ADDRESS}:{FRONTEND_PORT}"
                + "/user/subscription/payment?success=true&agency=False&session_id={CHECKOUT_SESSION_ID}"
            )
            cancel_url = (
                f"{URL_SCHEME}://{FRONTEND_ADDRESS}:{FRONTEND_PORT}"
                + "/user/subscription/payment?success=false&user_group=False"
            )

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    (
                        {"price": PRICE_ID, "quantity": 1}
                        if not prorated
                        else {
                            "price": PRICE_ID,
                        }
                    )
                ],
                mode="subscription",
                payment_method_types=["card"],
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return Response({"url": checkout_session.url})
        except Exception as e:
            logging.error(str(e))
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST"])
@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_SECRET_WEBHOOK
        )
    except ValueError:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return Response(status=401)

    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        # Get the Invoice object from the Subscription object
        invoice = stripe.Invoice.retrieve(subscription["latest_invoice"])
        # Get the Charge object from the Invoice object
        charge = stripe.Charge.retrieve(invoice["charge"])

        # Get paying user
        customer = stripe.Customer.retrieve(subscription["customer"])
        USER = CustomUser.objects.filter(email=customer.email).first()

        product = subscription["items"]["data"][0]
        SUBSCRIPTION_PLAN = SubscriptionPlan.objects.get(
            stripe_product_id=product["plan"]["product"]
        )
        SUBSCRIPTION = UserSubscription.objects.create(
            subscription=SUBSCRIPTION_PLAN,
            annual=product["plan"]["interval"] == "year",
            valid=True,
            user=USER,
            stripe_id=subscription["id"],
        )
        email = SubscriptionAvailedEmail()

        paid = {
            "amount": charge["amount"] / 100,
            "currency": str(charge["currency"]).upper(),
        }

        email.context = {
            "user": USER,
            "subscription_plan": SUBSCRIPTION_PLAN,
            "subscription": SUBSCRIPTION,
            "price_paid": paid,
        }
        email.send(to=[customer.email])

        # Clear cache
        cache.delete(f"billing_user:{USER.id}")
        cache.delete(f"subscriptions_user:{USER.id}")

    # On chargebacks/refunds, invalidate the subscription
    elif event["type"] == "charge.refunded":
        charge = event["data"]["object"]

        # Get the Invoice object from the Charge object
        invoice = stripe.Invoice.retrieve(charge["invoice"])

        # Check if the subscription exists
        SUBSCRIPTION = UserSubscription.objects.filter(
            stripe_id=invoice["subscription"]
        ).first()

        if not (SUBSCRIPTION):
            return HttpResponse(status=404)

        if SUBSCRIPTION.user:
            USER = SUBSCRIPTION.user

            # Mark refunded subscription as invalid
            SUBSCRIPTION.valid = False
            SUBSCRIPTION.save()

            SUBSCRIPTION_PLAN = SUBSCRIPTION.subscription

            refund = {
                "amount": charge["amount_refunded"] / 100,
                "currency": str(charge["currency"]).upper(),
            }

            # Send an email
            email = SubscriptionRefundedEmail()

            email.context = {
                "user": USER,
                "subscription_plan": SUBSCRIPTION_PLAN,
                "refund": refund,
            }

            email.send(to=[USER.email])

            # Clear cache
            cache.delete(f"billing_user:{USER.id}")

        elif SUBSCRIPTION.user_group:
            OWNER = SUBSCRIPTION.user_group.owner
            # Mark refunded subscription as invalid
            SUBSCRIPTION.valid = False
            SUBSCRIPTION.save()

            SUBSCRIPTION_PLAN = SUBSCRIPTION.subscription

            refund = {
                "amount": charge["amount_refunded"] / 100,
                "currency": str(charge["currency"]).upper(),
            }

            # Send en email
            email = SubscriptionRefundedEmail()

            email.context = {
                "user": OWNER,
                "subscription_plan": SUBSCRIPTION_PLAN,
                "refund": refund,
            }
            email.send(to=[OWNER.email])

            # Clear cache
            cache.delete(f"billing_user:{USER.id}")
            cache.delete(f"subscriptions_user:{USER.id}")

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]

        # Check if the subscription exists
        SUBSCRIPTION = UserSubscription.objects.filter(
            stripe_id=subscription["id"]
        ).first()

        if not (SUBSCRIPTION):
            return HttpResponse(status=404)

        # Check if a subscription has been upgraded/downgraded
        new_stripe_product_id = subscription["items"]["data"][0]["plan"]["product"]
        current_stripe_product_id = SUBSCRIPTION.subscription.stripe_product_id
        if new_stripe_product_id != current_stripe_product_id:
            SUBSCRIPTION_PLAN = SubscriptionPlan.objects.get(
                stripe_product_id=new_stripe_product_id
            )
            SUBSCRIPTION.subscription = SUBSCRIPTION_PLAN
            SUBSCRIPTION.save()
            # TODO: Add a plan upgraded email message here

        # Subscription activation/reactivation
        if subscription["status"] == "active":
            SUBSCRIPTION.valid = True
            SUBSCRIPTION.save()

            if SUBSCRIPTION.user:
                USER = SUBSCRIPTION.user

                # Clear cache
                cache.delete(f"billing_user:{USER.id}")
                cache.delete(f"subscriptions_user:{USER.id}")

            elif SUBSCRIPTION.user_group:
                OWNER = SUBSCRIPTION.user_group.owner

                # Clear cache
                cache.delete(f"billing_user:{OWNER.id}")
                cache.delete(f"subscriptions_usergroup:{SUBSCRIPTION.user_group.id}")

            # TODO: Add notification here to inform users if their plan has been reactivated

        elif subscription["status"] == "past_due":
            # TODO: Add notification here to inform users if their payment method for an existing subscription payment is failing
            pass

        # If subscriptions get cancelled due to non-payment, invalidate the UserSubscription
        elif subscription["status"] == "cancelled":
            if SUBSCRIPTION.user:
                USER = SUBSCRIPTION.user

                # Mark refunded subscription as invalid
                SUBSCRIPTION.valid = False
                SUBSCRIPTION.save()

                SUBSCRIPTION_PLAN = SUBSCRIPTION.subscription

                # Send an email
                email = SubscriptionCancelledEmail()

                email.context = {
                    "user": USER,
                    "subscription_plan": SUBSCRIPTION_PLAN,
                    "user_group": False,
                }
                email.send(to=[USER.email])

                # Clear cache
                cache.delete(f"billing_user:{USER.id}")
                cache.delete(f"subscriptions_user:{USER.id}")

            elif SUBSCRIPTION.user_group:
                OWNER = SUBSCRIPTION.user_group.owner

                # Mark refunded subscription as invalid
                SUBSCRIPTION.valid = False
                SUBSCRIPTION.save()

                # Send an email
                email = SubscriptionCancelledEmail()

                SUBSCRIPTION_PLAN = SUBSCRIPTION.subscription

                email.context = {"user": OWNER, "subscription_plan": SUBSCRIPTION_PLAN}
                email.send(to=[OWNER.email])

                # Clear cache
                cache.delete(f"billing_user:{OWNER.id}")
                cache.delete(f"subscriptions_usergroup:{SUBSCRIPTION.user_group.id}")

    # If a subscription gets cancelled, invalidate it
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]

        # Check if the subscription exists
        SUBSCRIPTION = UserSubscription.objects.filter(
            stripe_id=subscription["id"]
        ).first()

        if not (SUBSCRIPTION):
            return HttpResponse(status=404)

        if SUBSCRIPTION.user:
            USER = SUBSCRIPTION.user

            # Mark refunded subscription as invalid
            SUBSCRIPTION.valid = False
            SUBSCRIPTION.save()

            SUBSCRIPTION_PLAN = SUBSCRIPTION.subscription

            # Send an email
            email = SubscriptionCancelledEmail()

            email.context = {
                "user": USER,
                "subscription_plan": SUBSCRIPTION_PLAN,
                "user_group": False,
            }
            email.send(to=[USER.email])

            # Clear cache
            cache.delete(f"billing_user:{USER.id}")

        elif SUBSCRIPTION.user_group:
            OWNER = SUBSCRIPTION.user_group.owner

            # Mark refunded subscription as invalid
            SUBSCRIPTION.valid = False
            SUBSCRIPTION.save()

            # Send an email
            email = SubscriptionCancelledEmail()

            SUBSCRIPTION_PLAN = SUBSCRIPTION.subscription

            email.context = {"user": OWNER, "subscription_plan": SUBSCRIPTION_PLAN}
            email.send(to=[OWNER.email])

            # Clear cache
            cache.delete(f"billing_user:{OWNER.id}")

    # Passed signature verification
    return HttpResponse(status=200)
