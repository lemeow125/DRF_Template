from celery import shared_task


@shared_task
def get_user_subscription(user_id):
    from subscriptions.models import UserSubscription
    from accounts.models import CustomUser

    USER = CustomUser.objects.get(id=user_id)

    # Get a list of subscriptions for the specified user
    active_subscriptions = None
    if USER.user_group:
        active_subscriptions = UserSubscription.objects.filter(
            user_group=USER.user_group, valid=True
        )
    else:
        active_subscriptions = UserSubscription.objects.filter(user=USER, valid=True)

    # Return first valid subscription if there is one
    if len(active_subscriptions) > 0:
        return active_subscriptions[0]
    else:
        return None


@shared_task
def get_user_group_subscription(user_group):
    from subscriptions.models import UserSubscription
    from user_groups.models import UserGroup

    USER_GROUP = UserGroup.objects.get(id=user_group)
    # Get a list of subscriptions for the specified user
    active_subscriptions = None
    active_subscriptions = UserSubscription.objects.filter(
        user_group=USER_GROUP, valid=True
    )

    # Return first valid subscription if there is one
    if len(active_subscriptions) > 0:
        return active_subscriptions[0]
    else:
        return None
