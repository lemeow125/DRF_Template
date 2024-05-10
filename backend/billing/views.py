from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from config.settings import STRIPE_SECRET_KEY
from django.core.cache import cache
from datetime import datetime
import stripe


# Make sure to set your secret key
stripe.api_key = STRIPE_SECRET_KEY


class BillingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        requesting_user = self.request.user

        if requesting_user.user_group:
            email = requesting_user.user_group.owner.email
        else:
            email = requesting_user.email

        # Check cache
        key = f'billing_user:{requesting_user.id}'
        billing_history = cache.get(key)

        if not billing_history:
            # List customers and filter by email
            customers = stripe.Customer.list(limit=1, email=email)

            if customers:
                customer = customers.data[0]

                # List customers and filter by email
                customers = stripe.Customer.list(limit=1, email=email)

                if len(customers.data) > 0:
                    # Retrieve the customer's charges (billing history)
                    charges = stripe.Charge.list(
                        limit=10, customer=customer.id)

                    # Prepare the response
                    billing_history = [
                        {
                            'email': charge['billing_details']['email'],
                            'amount_charged': int(charge['amount']/100),
                            'paid': charge['paid'],
                            'refunded': int(charge['amount_refunded']/100) > 0,
                            'amount_refunded': int(charge['amount_refunded']/100),
                            'last_4': charge['payment_method_details']['card']['last4'],
                            'receipt_link': charge['receipt_url'],
                            'timestamp': datetime.fromtimestamp(charge['created']).strftime("%m-%d-%Y %I:%M %p"),
                        } for charge in charges.auto_paging_iter()
                    ]

                    cache.set(key, billing_history, 60*60)

        return Response(billing_history, status=status.HTTP_200_OK)
