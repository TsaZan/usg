from django.apps import AppConfig


class UgcUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ugc_users"
    verbose_name = "UGC Users"

    def ready(self):
        import ugc_users.signals  # noqa
