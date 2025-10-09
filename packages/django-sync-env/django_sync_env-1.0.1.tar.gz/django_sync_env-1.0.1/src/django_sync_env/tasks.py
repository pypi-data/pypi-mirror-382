from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command
from django_sync_env.constants import (
    BACKUP_DATABASE_MANAGEMENT_COMMAND_NAME, BACKUP_MEDIA_MANAGEMENT_COMMAND_NAME,
)

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=2, ignore_result=True)
def backup_databases(self):
    """Backup all databases in the django settings partial to a .psql.bin.gz file in app/backups/"""
    try:
        call_command(BACKUP_DATABASE_MANAGEMENT_COMMAND_NAME)

    except Exception as e:
        logger.error(e)


@shared_task(bind=True, max_retries=2, ignore_result=True)
def backup_media(self):
    """Backup the app/media/ directory and the contents to a .tar file in app/backups/"""
    try:
        call_command(BACKUP_MEDIA_MANAGEMENT_COMMAND_NAME)

    except Exception as e:
        logger.error(e)
