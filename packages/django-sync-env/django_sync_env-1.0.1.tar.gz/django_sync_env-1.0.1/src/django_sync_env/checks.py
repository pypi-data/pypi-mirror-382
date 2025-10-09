import re

from django.core.checks import Tags, Warning, register

from syncenv import settings

W001 = Warning(
    "SYNC_ENV_BACKUP_CONFIG setting has not be configured",
    hint="Set up settings.SYNC_ENV_BACKUP_CONFIG see syncenv readme",
    id="syncenv.W001",
)

W002 = Warning(
    "SYNC_ENV_RESTORE_CONFIG setting has not be configured",
    hint="Set up settings.SYNC_ENV_RESTORE_CONFIG see syncenv readme",
    id="syncenv.W002",
)

W005 = Warning(
    "Invalid DATE_FORMAT parameter",
    hint="settings.SYNC_ENV_DATE_FORMAT can contain only [A-Za-z0-9%_-]",
    id="syncenv.W005",
)


@register(Tags.compatibility)
def check_settings(app_configs, **kwargs):
    errors = []

    if not settings.SYNC_ENV_BACKUP_CONFIG:
        errors.append(W001)

    if not settings.SYNC_ENV_RESTORE_CONFIG:
        errors.append(W001)

    if re.search(r"[^A-Za-z0-9%_-]", settings.DATE_FORMAT):
        errors.append(W005)

    return errors
