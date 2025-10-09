"""
Restore database.
"""
import datetime
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
    help = """Restore a database backup from storage, encrypted and/or compressed."""
    content_type = "db"
    logger = logging.getLogger("sync_env")

    option_list = BaseSyncBackupCommand.option_list + (
        make_option("-d", "--database",
                    help="Database to restore",
                    ),
        make_option("-i", "--input-filename",
                    help="Specify filename of a backup to restore",
                    ),
        make_option("-I", "--input-path",
                    help="Specify the local path to restore from",
                    ),
        make_option("-e", "--environment",
                    help="If backup file is not specified, filter the existing ones with the given environment",
                    ),
        make_option("-z", "--uncompress",
                    action="store_true",
                    default=True,
                    help="Uncompress gzip data before restoring",
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
                self._restore_interactive_backup(options)
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

    def _restore_interactive_backup(self, options):
        self.logger.info("Please select a database to restore")

        environment_choices = sync_env_settings.SYNC_ENV_ENVIRONMENTS.keys()

        environments = [
            inquirer.List(
                "environment",
                message="Select a environment to restore from",
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
                message="Select a database backup",
                choices=db_choices,
            ),
        ]

        selected_database_backup = inquirer.prompt(db_backups)
        if not selected_database_backup:
            self.logger.error("no db backup selected, exiting")
            return
        input_database_filename = selected_database_backup.get('db_backup')

        database_options = settings.DATABASES.keys()
        databases = [
            inquirer.List(
                "db",
                message="Select a database to restore to",
                choices=database_options,
            ),
        ]

        selected_database = inquirer.prompt(databases)
        if not selected_database:
            self.logger.error("no db selected, exiting")
            return
        database_name = selected_database.get('db')

        self._restore_backup(storage, input_database_filename, database_name, environment)

    def _restore_backup(self, storage, input_database_filename, database_name, environment):
        """Restore the specified database."""
        input_filename, input_file = self._get_backup_file(
            storage, input_database_filename
        )
        self.logger.info(f"Restoring backup for database {input_database_filename} from {environment}")

        if self.uncompress:
            uncompressed_file, input_filename = utils.uncompress_file(
                input_file, input_filename
            )
            input_file.close()
            input_file = uncompressed_file

        self.logger.info("Restore tempfile created: %s", utils.handle_size(input_file))
        if self.noinput:
            self._ask_confirmation()

        input_file.seek(0)
        self.connector = get_connector(database_name)
        self.connector.restore_dump(input_file)
        self.logger.info(
            f"Completed db restore: {input_database_filename} [{utils.handle_size(input_file)}] => {database_name} "
        )
