from celery import shared_task


@shared_task
def get_paying_users():
    from subscriptions.models import UserSubscription
    # Get a list of user subscriptions
    active_subscriptions = UserSubscription.objects.filter(
        valid=True).distinct('user')

    # Get paying users
    active_users = []

    # Paying regular users
    active_users += [
        subscription.user.id for subscription in active_subscriptions if subscription.user is not None and subscription.user.user_group is None]

    # Paying users within groups
    active_users += [
        subscription.user_group.members for subscription in active_subscriptions if subscription.user_group is not None and subscription.user is None]

    # Return paying users
    return active_users
