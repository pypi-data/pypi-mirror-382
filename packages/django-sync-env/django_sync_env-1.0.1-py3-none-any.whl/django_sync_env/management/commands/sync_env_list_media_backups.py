"""
List backups.
"""
import datetime
from django_sync_env.storage import get_storage
from django_sync_env.management.commands._base import BaseSyncBackupCommand, make_option, ROW_TEMPLATE
from django_sync_env import settings
import logging


class Command(BaseSyncBackupCommand):
    help = "Connect to configured storage endpoints to get a list of media backups"
    logger = logging.getLogger("sync_env")
    storages = []
    option_list = ()

    def custom_sort(self, item):
        """Custom sort method to return the file list in environment grouped descending order based on date"""
        date_format = settings.DISPLAY_DATE_TIME_FORMAT
        # First, sort by the 'environment' key
        environment_key = item['environment']
        # Second, sort by the 'datetime' key (converted to datetime, as it's a string)
        date_key = datetime.datetime.strptime(item['datetime'], date_format)
        return environment_key, date_key

    def handle(self, **options):
        self.logger.info("Connecting to configured storage endpoints to get a list of media backups")

        files_attr = []
        for idx, (env, config) in enumerate(settings.SYNC_ENV_ENVIRONMENTS.items()):
            options.update({"content_type": "media"})
            storage = get_storage(env, config)
            if not storage:
                continue
            files_attr += self.get_backups_attrs(storage, options, env)
            # Sort the list of dictionaries using the custom_sort function
            files_attr = sorted(files_attr, key=self.custom_sort, reverse=True)

        title = ROW_TEMPLATE.format(
            name="Name",
            environment="Environment",
            datetime="Date"
        )
        line = '-' * len(title)
        self.stdout.write(line)
        self.stdout.write(title)
        self.stdout.write(line)

        for idx, file_attr in enumerate(files_attr):
            row = ROW_TEMPLATE.format(**file_attr)
            self.stdout.write(row)

        self.stdout.write('-' * settings.PRINT_ROW_LENGTH)
