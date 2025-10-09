"""Apps for SyncEnv"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from django_sync_env import log


class SyncEnvConfig(AppConfig):
    """
    Config for SyncEnv
    """

    name = "django_sync_env"
    label = "django_sync_env"
    verbose_name = gettext_lazy("sync env")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        log.load_logger()
