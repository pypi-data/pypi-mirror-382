"""
Restore media files.
"""
import datetime
import logging
import tarfile
import inquirer
from django.conf import settings
from django.core.files.storage import default_storage

from django_sync_env import utils
from django_sync_env.storage import get_storage
from django_sync_env.management.commands._base import BaseSyncBackupCommand, make_option
from django_sync_env import settings as sync_env_settings


class Command(BaseSyncBackupCommand):
    help = """Restore a media backup from storage, encrypted and/or compressed."""
    content_type = "media"
    logger = logging.getLogger("sync_env")

    option_list = (
        make_option(
            "-i",
            "--input-filename",
            action="store",
            help="Specify filename to backup from",
        ),
        make_option(
            "-I", "--input-path",
            help="Specify path on local filesystem to backup from",
        ),
        make_option(
            "-s",
            "--servername",
            help="If backup file is not specified, filter the existing ones with the given servername",
        ),
        make_option(
            "-z",
            "--uncompress",
            action="store_true",
            help="Uncompress gzip data before restoring",
        ),
        make_option(
            "-r", "--replace",
            help="Replace existing files",
            action="store_true",
        ),
    )

    def handle(self, *args, **options):
        """Django command handler."""
        self._set_logger_level()

        self.verbosity = int(options.get("verbosity"))
        self.quiet = options.get("quiet")
        self.servername = options.get("servername")
        self.uncompress = options.get("uncompress")
        self.filename = options.get("input_filename")
        self.path = options.get("input_path")
        self.replace = options.get("replace")
        self.passphrase = options.get("passphrase")
        self.interactive = options.get("interactive")
        self.media_storage = default_storage
        self.noinput = options.get("noinput")

        options['content_type'] = 'media'

        if self.noinput:
            self._restore_interactive_backup(options)
            return

        self._restore_backup()

    def _upload_file(self, name, media_file):
        if self.media_storage.exists(name):
            if not self.replace:
                self.logger.info(f"{name} - skipped, already exists")
                return
            self.media_storage.delete(name)
            self.logger.info(f"{name} - deleted")
        self.media_storage.save(name, media_file)
        self.logger.info(f"{name} - uploaded")

    def _restore_interactive_backup(self, options):
        self.logger.info("Please select media to restore")
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
        if not storage:
            self.logger.error(f'Unable to connect to storage for environment: {environment}, check config')
            return

        media_backups = self.get_backups_attrs(storage, options, environment)
        date_format = sync_env_settings.DISPLAY_DATE_TIME_FORMAT
        media_backups = sorted(
            media_backups,
            key=lambda x: datetime.datetime.strptime(x['datetime'], date_format),
            reverse=True
        )

        media_choices = [x['name'] for x in media_backups]
        media_backups = [
            inquirer.List(
                "media_backup",
                message="Select a media backup",
                choices=media_choices,
            ),
        ]

        selected_media_backup = inquirer.prompt(media_backups)
        if not selected_media_backup:
            self.logger.error("no media backup selected, exiting")
            return

        selected_media_backup_filename = selected_media_backup.get('media_backup')

        self._restore_backup(storage, selected_media_backup_filename, environment)

    def _restore_backup(self, storage, selected_media_backup_filename, environment):
        self.logger.info("Restoring backup for media files...")
        input_filename, input_file = self._get_backup_file(
            # servername=self.servername
            storage, selected_media_backup_filename
        )
        self.logger.info(f"Restoring media backup {input_filename} from {environment}")
        self.logger.info("Backup size: %s", utils.handle_size(input_file))

        self._ask_confirmation()

        input_file.seek(0)
        tar_file = tarfile.open(fileobj=input_file, mode="r:gz")

        # Restore file 1 by 1
        for media_file_info in tar_file:
            if media_file_info.path == "media":
                continue  # Don't copy root directory
            media_file = tar_file.extractfile(media_file_info)
            if media_file is None:
                continue  # Skip directories
            name = media_file_info.path.replace("media/", "")
            self._upload_file(name, media_file)
