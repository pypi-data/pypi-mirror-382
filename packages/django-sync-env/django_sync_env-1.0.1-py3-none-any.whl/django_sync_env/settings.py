# DO NOT IMPORT THIS BEFORE django.configure() has been run!

import socket
import tempfile

from django.conf import settings

ENVIRONMENT = getattr(settings, "ENVIRONMENT")
SYNC_ENV_PROJECT_NAME = getattr(settings, "PROJECT_NAME")
SYNC_ENV_BACKUP_CONFIG = getattr(settings, "SYNC_ENV_BACKUP_CONFIG")
SYNC_ENV_RESTORE_CONFIG = getattr(settings, "SYNC_ENV_RESTORE_CONFIG")

SYNC_ENV_NOTIFICATION_CONFIG = getattr(settings, "SYNC_ENV_NOTIFICATION_CONFIG", {})

SYNC_ENV_ENVIRONMENTS = {}

# merge backup and restore locations so we can pull from local backups as well as remote backups
SYNC_ENV_ENVIRONMENTS.update(SYNC_ENV_BACKUP_CONFIG)
SYNC_ENV_ENVIRONMENTS.update(SYNC_ENV_RESTORE_CONFIG)

DATABASES = getattr(settings, "DATABASES").keys()

# Fake host
HOSTNAME = socket.gethostname()

# Directory to use for temporary files
TMP_DIR = tempfile.gettempdir()
TMP_FILE_MAX_SIZE = 10 * 1024 * 1024
TMP_FILE_READ_SIZE = 1024 * 1000

# Number of old backup files to keep
CLEANUP_KEEP = getattr(settings, "SYNC_ENV_CLEANUP_KEEP", 10)
CLEANUP_KEEP_MEDIA = getattr(settings, "SYNC_ENV_CLEANUP_KEEP_MEDIA", CLEANUP_KEEP)
CLEANUP_KEEP_FILTER = getattr(settings, "SYNC_ENV_CLEANUP_KEEP_FILTER", lambda x: False)

MEDIA_PATH = settings.MEDIA_ROOT

DATE_FORMAT = "%d-%m-%Y-%H%M%S"

DISPLAY_DATE_TIME_FORMAT = "%d %B %y %X"  # e.g. 14 April 2025 14:46:25
PRINT_ROW_LENGTH = 142 # the total row length of ROW_TEMPLATE

FILENAME_TEMPLATE = "{projectname}-{environment}-{databasename}-{datetime}.{extension}"

MEDIA_FILENAME_TEMPLATE = "{projectname}-{environment}-media-{datetime}.{extension}"

CONNECTORS = getattr(settings, "SYNC_ENV_CONNECTORS", {})

CUSTOM_CONNECTOR_MAPPING = getattr(settings, "SYNC_ENV_CONNECTOR_MAPPING", {})

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
