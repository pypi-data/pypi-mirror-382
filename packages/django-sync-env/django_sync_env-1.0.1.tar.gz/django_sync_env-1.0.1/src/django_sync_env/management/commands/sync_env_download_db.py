"""
Restore database.
"""
import datetime
import os

from django.conf import settings
from django.core.management.base import CommandError
from django.db import connection

import inquirer
import logging
from django_sync_env import utils
from django_sync_env import settings as sync_env_settings
from django_sync_env.db.base import get_connector
from django_sync_env.storage import StorageError, get_storage
from django_sync_env.management.commands._base import BaseSyncBackupCommand, make_option


class Command(BaseSyncBackupCommand):
    help = """Download a database backup from storage, to local storage."""
    content_type = "db"
    logger = logging.getLogger("sync_env")

    option_list = BaseSyncBackupCommand.option_list + (
        make_option("-O", "--output-path",
                    help="Specify the local path to download to",
                    ),
    )

    def handle(self, *args, **options):
        """Django command handler."""
        self.verbosity = int(options.get("verbosity"))
        self.quiet = options.get("quiet")
        self._set_logger_level()

        try:
            connection.close()
            self.environment = options.get("environment")
            self.uncompress = options.get("uncompress")
            self.noinput = options.get("noinput")
            self.input_database_name = options.get("database")
            options['content_type'] = 'db'

            if self.noinput:
                self._download_interactive_backup(options)
                return

            if not self.environment:
                self.logger.error("An environment and database must be specified")
                exit(1)

            environment = self.environment
            storage_config = utils.get_storage_config(environment, sync_env_settings.SYNC_ENV_ENVIRONMENTS)
            storage = get_storage(environment, storage_config)
            if storage:
                self._restore_backup(storage, self.input_database_name, environment)
            else:
                self.logger.error(f'Unable to connect to storage for environment: {environment}, check config')

        except StorageError as err:
            raise CommandError(err) from err

    def _get_database(self, database_name: str):
        """Get the database to restore."""
        if not database_name:
            if len(settings.DATABASES) > 1:
                errmsg = (
                    "Because this project contains more than one database, you"
                    " must specify the --database option."
                )
                raise CommandError(errmsg)
            database_name = list(settings.DATABASES.keys())[0]
        if database_name not in settings.DATABASES:
            raise CommandError(f"Database {database_name} does not exist.")
        return database_name, settings.DATABASES[database_name]

    def _download_interactive_backup(self, options):
        self.logger.info("Please select a database to restore")

        environment_choices = sync_env_settings.SYNC_ENV_RESTORE_CONFIG.keys()

        environments = [
            inquirer.List(
                "environment",
                message="Select a environment to download a database from",
                choices=environment_choices,
            ),
        ]

        selected_environment = inquirer.prompt(environments)

        if not selected_environment:
            self.logger.error("No environment selected, exiting")
            return

        environment = selected_environment.get('environment')
        storage_config = utils.get_storage_config(environment, sync_env_settings.SYNC_ENV_ENVIRONMENTS)
        storage = get_storage(environment, storage_config)

        database_backups = self.get_backups_attrs(storage, options, environment)
        date_format = sync_env_settings.DISPLAY_DATE_TIME_FORMAT
        database_backups = sorted(
            database_backups,
            key=lambda x: datetime.datetime.strptime(x['datetime'], date_format),
            reverse=True
        )

        db_choices = [x['name'] for x in database_backups]
        db_backups = [
            inquirer.List(
                "db_backup",
                message="Select a database to download",
                choices=db_choices,
            ),
        ]

        selected_database_backup = inquirer.prompt(db_backups)
        if not selected_database_backup:
            self.logger.error("no db backup selected, exiting")
            return
        input_database_filename = selected_database_backup.get('db_backup')
        self._download_backup(storage, input_database_filename, environment)

    def _download_backup(self, storage, input_database_filename, environment):
        """Restore the specified database."""
        input_filename, input_file = self._get_backup_file(
            storage, input_database_filename
        )
        self.logger.info(f"Download backup for database {input_database_filename} from {environment}")
        if self.uncompress:
            uncompressed_file, input_filename = utils.uncompress_file(
                input_file, input_filename
            )
            input_file.close()
            input_file = uncompressed_file

        self.logger.info("Tempfile created: %s", utils.handle_size(input_file))

        input_file.seek(0)
        output_filename = input_file.name

        if hasattr(settings, 'SYNC_ENV_DEV_STORAGE_LOCATION'):
            output_file_path = os.path.join(settings.SYNC_ENV_DEV_STORAGE_LOCATION, output_filename)
        else:
            output_file_path = os.path.join('/tmp', output_filename)

        with open(output_file_path, 'wb') as f:
            f.write(input_file.read())

        self.logger.info(
            f"Completed db download to: {output_file_path} "
        )
