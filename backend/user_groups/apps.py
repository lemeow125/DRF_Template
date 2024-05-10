from django.apps import AppConfig


class EnterpriseGroupsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_groups"

    def ready(self):
        import user_groups.signals
