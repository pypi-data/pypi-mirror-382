"""
Abstract Command.
"""
import logging
import sys
from optparse import make_option as optparse_make_option
from shutil import copyfileobj
import inquirer
import django
from django.core.management.base import BaseCommand, CommandError

from django_sync_env import settings
from django_sync_env import utils
from django_sync_env.storage import StorageError

ROW_TEMPLATE = "{name:80} {environment:40} {datetime:20}"
FILTER_KEYS = ("encrypted", "compressed", "content_type", "database")
USELESS_ARGS = ("callback", "callback_args", "callback_kwargs", "metavar")
TYPES = {
    "string": str,
    "int": int,
    "long": int,
    "float": float,
    "complex": complex,
    "choice": list,
}

LOGGING_VERBOSITY = {
    0: logging.WARN,
    1: logging.INFO,
    2: logging.DEBUG,
    3: logging.DEBUG,
}


def make_option(*args, **kwargs):
    return args, kwargs


class BaseSyncBackupCommand(BaseCommand):
    """
    Base command class used for create all syncenv command.
    """

    base_option_list = (
        make_option(
            "--noinput",
            action="store_false",
            dest="noinput",
            default=True,
            help="Tells Django to NOT prompt the user for input of any kind.",
        ),
        make_option(
            "-q",
            "--quiet",
            action="store_true",
            default=False,
            help="Tells Django to NOT output other text than errors.",
        ),
    )
    option_list = ()

    verbosity = 1
    quiet = False
    storages = []
    logger = logging.getLogger("syncenv.command")

    def __init__(self, *args, **kwargs):
        self.option_list = self.base_option_list + self.option_list
        if django.VERSION < (1, 10):
            options = tuple(
                optparse_make_option(*_args, **_kwargs)
                for _args, _kwargs in self.option_list
            )

            self.option_list = options + BaseCommand.option_list
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        for args, kwargs in self.option_list:
            kwargs = {
                k: v
                for k, v in kwargs.items()
                if not k.startswith("_") and k not in USELESS_ARGS
            }
            parser.add_argument(*args, **kwargs)

    def _set_logger_level(self):
        level = 60 if self.quiet else LOGGING_VERBOSITY[int(self.verbosity)]
        self.logger.setLevel(level)

    def _ask_confirmation(self):
        confirmation = inquirer.prompt([inquirer.Confirm("continue", message="Are you sure you want to continue?")])
        if not confirmation.get('continue', False):
            self.logger.info("Quitting")
            sys.exit(0)

    def read_from_storage(self, storage, path):
        return storage.read_file(path)

    def write_to_storage(self, storage, file, path):
        self.logger.info(f"Writing file to {storage.storage.location}/{path}")
        storage.write_file(file, path)

    def read_local_file(self, path):
        """Open file in read mode on local filesystem."""
        return open(path, "rb")

    def write_local_file(self, outputfile, path):
        """Write file to the desired path."""
        if not self.quiet:
            self.logger.info(f"Writing file to disk at {path}")
        outputfile.seek(0)
        with open(path, "wb") as fd:
            copyfileobj(outputfile, fd)

    def _get_backup_file(self, storage, database_filename):
        input_file = self.read_from_storage(storage, database_filename)
        return database_filename, input_file

    def _get_latest_backup_file(self, storage, database, environment, content_type):
        try:
            input_filename = storage.get_latest_backup(
                compressed=self.uncompress,
                content_type=content_type,
                database=database,
                environment=environment,
            )
        except StorageError as err:
            raise CommandError(err.args[0]) from err

        input_file = self.read_from_storage(input_filename)
        return input_filename, input_file

    def get_backups_attrs(self, storage, options, environment):
        filters = {k: v for k, v in options.items() if k in FILTER_KEYS}

        backups = []
        filenames = storage.list_backups(**filters)
        for filename in filenames:
            backups.append(
                {
                    "environment": environment,
                    "datetime": utils.filename_to_date(filename).strftime(settings.DISPLAY_DATE_TIME_FORMAT),
                    "name": filename,
                }
            )
        return backups

    def _cleanup_old_backups(self, database=None, environment=None):
        """
        Cleanup old backups, keeping the number of backups specified by
        SYNC_ENV_CLEANUP_KEEP and any backups that occur on first of the month.
        """
        print('self.storage: ', self.storage)
        print('self.compress: ', self.compress)
        print('self.content_type: ', self.content_type)
        print('database: ', database)
        print('environment: ', environment)
        self.storage.clean_old_backups(
            compressed=self.compress,
            content_type=self.content_type,
            database=database,
            environment=environment,
        )

    def get_version(self):
        """returns the version of the django_sync_env app"""
        from django_sync_env import VERSION
        return utils.get_version(VERSION)
