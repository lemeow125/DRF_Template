from subscriptions.models import SubscriptionPlan
from accounts.models import CustomUser
from .models import UserGroup
from subscriptions.tasks import get_user_group_subscription
from django.db.models.signals import m2m_changed, post_migrate
from django.dispatch import receiver
from config.settings import STRIPE_SECRET_KEY, ROOT_DIR
import os
import json
import stripe

stripe.api_key = STRIPE_SECRET_KEY


@receiver(m2m_changed, sender=UserGroup.managers.through)
def update_group_managers(sender, instance, action, **kwargs):
    # When adding new managers to a UserGroup, associate them with it
    if action == "post_add":
        # Get the newly added managers
        new_managers = kwargs.get("pk_set", set())
        for manager in new_managers:
            # Retrieve the member
            USER = CustomUser.objects.get(pk=manager)
            if not USER.user_group:
                # Update their group assiociation
                USER.user_group = instance
                USER.save()
            if USER not in instance.members.all():
                instance.members.add(USER)
    # When removing managers from a UserGroup, remove their association with it
    elif action == "post_remove":
        for manager in kwargs["pk_set"]:
            # Retrieve the manager
            USER = CustomUser.objects.get(pk=manager)
            if USER not in instance.members.all():
                USER.user_group = None
                USER.save()


@receiver(m2m_changed, sender=UserGroup.members.through)
def update_group_members(sender, instance, action, **kwargs):
    # When adding new members to a UserGroup, associate them with it
    if action == "post_add":
        # Get the newly added members
        new_members = kwargs.get("pk_set", set())
        for member in new_members:
            # Retrieve the member
            USER = CustomUser.objects.get(pk=member)
            if not USER.user_group:
                # Update their group assiociation
                USER.user_group = instance
                USER.save()
    # When removing members from a UserGroup, remove their association with it
    elif action == "post_remove":
        for client in kwargs["pk_set"]:
            USER = CustomUser.objects.get(pk=client)
            if (
                USER not in instance.members.all()
                and USER not in instance.managers.all()
            ):
                USER.user_group = None
                USER.save()
    # Update usage records
    SUBSCRIPTION_GROUP = get_user_group_subscription(instance.id)
    if SUBSCRIPTION_GROUP:
        try:
            print(f"Updating usage record for UserGroup {instance.name}")
            # Update usage for members
            SUBSCRIPTION_ITEM = SUBSCRIPTION_GROUP.subscription
            stripe.SubscriptionItem.create_usage_record(
                SUBSCRIPTION_ITEM.stripe_id,
                quantity=len(instance.members.all()),
                action="set",
            )
        except:
            print(
                f"Warning: Unable to update usage record for SubscriptionGroup ID:{instance.id}"
            )


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == "agencies":
        with open(os.path.join(ROOT_DIR, "seed_data.json"), "r") as f:
            seed_data = json.loads(f.read())
            for user_group in seed_data["user_groups"]:
                OWNER = CustomUser.objects.filter(email=user_group["owner"]).first()
                USER_GROUP, CREATED = UserGroup.objects.get_or_create(
                    owner=OWNER,
                    agency_name=user_group["name"],
                )
                if CREATED:
                    print(f"Created UserGroup {USER_GROUP.agency_name}")

                # Add managers
                USERS = CustomUser.objects.filter(email__in=user_group["managers"])
                for USER in USERS:
                    if USER not in USER_GROUP.managers.all():
                        print(
                            f"Adding User {USER.full_name} as manager to UserGroup {USER_GROUP.agency_name}"
                        )
                        USER_GROUP.managers.add(USER)
                # Add members
                USERS = CustomUser.objects.filter(email__in=user_group["members"])
                for USER in USERS:
                    if USER not in USER_GROUP.members.all():
                        print(
                            f"Adding User {USER.full_name} as member to UserGroup {USER_GROUP.agency_name}"
                        )
                        USER_GROUP.clients.add(USER)
                USER_GROUP.save()
