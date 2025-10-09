"""
Save media files.
"""
import json
import logging
import os
import tarfile

from django.core.files.storage import default_storage
from django.core.management.base import CommandError

from django_sync_env import settings as sync_env_settings
from django_sync_env.storage import get_storage
from django_sync_env import utils
from django_sync_env.storage import StorageError
from django_sync_env.management.commands._base import BaseSyncBackupCommand, make_option
from django_sync_env.notifications import SyncEnvNotifications


class Command(BaseSyncBackupCommand):
    help = """Backup media files, gather all in a tarball and compress."""
    content_type = "media"
    logger = logging.getLogger("sync_env")
    notifications = SyncEnvNotifications()

    option_list = BaseSyncBackupCommand.option_list + (
        make_option(
            "-s",
            "--servername",
            help="Specify server name to include in backup filename",
        ),
        make_option(
            "-z",
            "--compress",
            help="Compress the archive",
            action="store_true",
            default=False,
        ),
        make_option(
            "-o", "--output-filename",
            default=None,
            help="Specify filename on storage",
        ),
        make_option(
            "-O",
            "--output-path",
            default=None,
            help="Specify where to store on local filesystem",
        ),
    )

    @utils.email_uncaught_exception
    def handle(self, **options):
        self._set_logger_level()

        self.verbosity = options.get("verbosity")
        self.quiet = options.get("quiet")
        self.compress = True  # always compress
        self.filename = options.get("output_filename")
        self.path = options.get("output_path")

        try:
            media_storage = default_storage
            environment = sync_env_settings.ENVIRONMENT
            storage_config = utils.get_storage_config(environment, sync_env_settings.SYNC_ENV_ENVIRONMENTS)
            storage = get_storage(environment, storage_config)

            if storage:
                self.backup_mediafiles(media_storage, storage)
                if self.notifications.enabled:
                    rich_text_blocks, text = self._format_slack_success_notification()
                    self.notifications.send_slack_message(blocks=rich_text_blocks, text=text)

                if options.get("clean"):
                    self._cleanup_old_backups(environment=environment)
            else:
                self.logger.error(f'Unable to connect to storage for environment: {environment}, check config')

        except StorageError as err:
            if self.notifications.enabled:
                rich_text_blocks, text = self._format_slack_failure_notification()
                self.notifications.send_slack_message(blocks=rich_text_blocks, text=text)
            raise CommandError(err) from err

    def _explore_storage(self, media_storage):
        """Generator of all files contained in media storage."""
        path = ""
        dirs = [path]
        while dirs:
            path = dirs.pop()
            try:
                subdirs, files = media_storage.listdir(path)
            except FileNotFoundError as err:
                self.logger.error(f'{err.strerror}, {err.filename}')
                exit(1)

            for media_filename in files:
                yield os.path.join(path, media_filename)
            dirs.extend([os.path.join(path, subdir) for subdir in subdirs])

    def _create_tar(self, media_storage, name):
        """Create TAR file."""
        fileobj = utils.create_spooled_temporary_file()
        mode = "w:gz" if self.compress else "w"
        tar_file = tarfile.open(name=name, fileobj=fileobj, mode=mode)
        for media_filename in self._explore_storage(media_storage):
            tarinfo = tarfile.TarInfo(media_filename)
            media_file = media_storage.open(media_filename)
            tarinfo.size = len(media_file)
            tar_file.addfile(tarinfo, media_file)
        # Close the TAR for writing
        tar_file.close()
        return fileobj

    def backup_mediafiles(self, media_storage, storage):
        """
        Create backup file and write it to storage.
        """
        # Check for filename option
        if self.filename:
            filename = self.filename
        else:
            extension = f"tar{'.gz' if self.compress else ''}"
            filename = utils.filename_generate(
                extension,
                content_type=self.content_type,
                environment=sync_env_settings.ENVIRONMENT,
            )

        self.logger.info(f"Creating {filename} backup")
        tarball = self._create_tar(media_storage, filename)
        self.logger.info(f"Backup size: {utils.handle_size(tarball)}")
        # Store backup
        tarball.seek(0)
        self.write_to_storage(storage, tarball, filename)
        self.logger.info(f"Media backup filename: {filename}")
        self.logger.info(f"Media backup completed: {utils.handle_size(tarball)}")

    @staticmethod
    def _format_slack_success_notification():
        """Returns the plain text and formatted dict object for a success rich-text Slack message"""
        emoji = sync_env_settings.SYNC_ENV_NOTIFICATION_CONFIG.get("PROJECT_EMOJI", "green_heart")
        plain_text_msg = f"{sync_env_settings.SYNC_ENV_PROJECT_NAME}:[{sync_env_settings.ENVIRONMENT}] - media assets backup was successful"
        rich_text_msg_blocks = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "emoji",
                                "name": emoji,
                            },
                            {
                                "type": "text",
                                "text": f" {sync_env_settings.SYNC_ENV_PROJECT_NAME}",
                                "style": {"bold": True},
                            },
                            {
                                "type": "text",
                                "text": f" [{sync_env_settings.ENVIRONMENT}] - Media assets backup was",
                            },
                            {
                                "type": "text",
                                "text": " Successful",
                                "style": {"bold": True},
                            },
                        ],
                    }
                ],
            }
        ]

        return json.dumps(rich_text_msg_blocks), plain_text_msg

    @staticmethod
    def _format_slack_failure_notification():
        """Returns the plain text and the formatted dict object for a warning based rich-text Slack message"""
        plain_text_msg = f"{sync_env_settings.SYNC_ENV_PROJECT_NAME}:[{sync_env_settings.ENVIRONMENT}] - media assets backup Failed!"
        rich_text_msg_blocks = [
            {
                "type": "rich_text",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "emoji",
                                "name": "warning"
                            },
                            {
                                "type": "text",
                                "text": f" {sync_env_settings.SYNC_ENV_PROJECT_NAME}",
                                "style": {
                                    "bold": True
                                }
                            },
                            {
                                "type": "text",
                                "text": f" [{sync_env_settings.ENVIRONMENT}] - Media assets backup"
                            },
                            {
                                "type": "text",
                                "text": " Failed!",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
                ]
            }
        ]
        return json.dumps(rich_text_msg_blocks), plain_text_msg
