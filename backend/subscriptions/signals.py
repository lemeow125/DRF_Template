from django.dispatch import receiver
from django.db.models.signals import post_migrate, post_save
from .models import UserSubscription, StripePrice, SubscriptionPlan
from django.core.cache import cache
from config.settings import STRIPE_SECRET_KEY
import stripe
stripe.api_key = STRIPE_SECRET_KEY

# Template for running actions after user have paid for a subscription


@receiver(post_save, sender=SubscriptionPlan)
def clear_cache_after_plan_updates(sender, instance, **kwargs):
    # Clear cache
    cache.delete('subscriptionplans')


@receiver(post_save, sender=UserSubscription)
def scan_after_payment(sender, instance, **kwargs):
    # If the updated/created subscription is valid
    if instance.valid and instance.user:
        # TODO: Add any Celery task actions here for regular subscription payees
        pass


@receiver(post_migrate)
def create_subscriptions(sender, **kwargs):
    if sender.name == 'subscriptions':
        print('Importing data from Stripe')
        created_prices = 0
        created_plans = 0
        skipped_prices = 0
        skipped_plans = 0
        products = stripe.Product.list(active=True)
        prices = stripe.Price.list(expand=["data.tiers"], active=True)

        # Create the StripePrice
        for price in prices['data']:
            annual = (price['recurring']['interval'] ==
                      'year') if price['recurring'] else False
            STRIPE_PRICE, CREATED = StripePrice.objects.get_or_create(
                stripe_price_id=price['id'],
                price=price['unit_amount'] / 100,
                annual=annual,
                lookup_key=price['lookup_key'],
                prorated=price['recurring']['usage_type'] == 'metered',
                currency=price['currency']
            )
            if CREATED:
                created_prices += 1
            else:
                skipped_prices += 1

        # Create the SubscriptionPlan
        for product in products['data']:
            ANNUAL_PRICE = None
            MONTHLY_PRICE = None
            for price in prices['data']:
                if price['product'] == product['id']:
                    STRIPE_PRICE = StripePrice.objects.get(
                        stripe_price_id=price['id'],
                    )
                    if STRIPE_PRICE.annual:
                        ANNUAL_PRICE = STRIPE_PRICE
                    else:
                        MONTHLY_PRICE = STRIPE_PRICE
            if ANNUAL_PRICE or MONTHLY_PRICE:
                SUBSCRIPTION_PLAN, CREATED = SubscriptionPlan.objects.get_or_create(
                    name=product['name'],
                    description=product['description'],
                    stripe_product_id=product['id'],
                    annual_price=ANNUAL_PRICE,
                    monthly_price=MONTHLY_PRICE,
                    group_exclusive=product['metadata']['group_exclusive'] == 'True'
                )
                if CREATED:
                    created_plans += 1
                else:
                    skipped_plans += 1
            # Skip over plans with missing pricing rates
            else:
                print('Skipping plan' +
                      product['name'] + 'with missing pricing data')

            # Assign the StripePrice to the SubscriptionPlan
            SUBSCRIPTION_PLAN.save()

        print('Created', created_plans, 'new plans')
        print('Skipped', skipped_plans, 'existing plans')
        print('Created', created_prices, 'new prices')
        print('Skipped', skipped_prices, 'existing prices')
