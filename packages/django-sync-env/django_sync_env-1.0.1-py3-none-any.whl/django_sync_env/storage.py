"""
Utils for handle files.
"""
import logging

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import storages
from django.core.files.storage.base import Storage as DjangoStorage

from django_sync_env import settings, utils

logger = logging.getLogger("sync_env")


def get_storage(environment, storage_config):
    """
    Get the specified storage configured with options.
    :param environment: The environment name for this storage object
    :type environment: ``str``

    :param storage_config: A list of storage configs
    :type storage_config: ``dict``

    :return: Storage configured
    :rtype: :dict
    """
    if type(storage_config) != dict:
        raise ImproperlyConfigured(
            "You must specify a dictionary to configure storage see sync readme", storage_config
        )
    required_keys = ["enabled", "storage_class", "options"]
    keys = storage_config.keys()
    for key in required_keys:
        if key not in keys:
            raise ImproperlyConfigured(
                f"You must specify {key} in storage_config see sync readme", storage_config
            )
    if type(storage_config['options']) != dict:
        raise ImproperlyConfigured(
            "You must specify an options dictionary to configure storage see sync readme", storage_config
        )

    enabled = storage_config.get('enabled', None)

    if not enabled:
        logger.error(f"{environment} it is missing configuration or is disabled")
        return

    storage = Storage(
        storages.create_storage(dict(BACKEND=storage_config["storage_class"], OPTIONS=storage_config["options"]))
    )
    return storage


class StorageError(Exception):
    pass


class FileNotFound(StorageError):
    pass


class Storage:
    """
    This object make high-level storage operations for upload/download or
    list and filter files. It uses a Django storage object for low-level
    operations.
    """

    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(__name__)
        return self._logger

    def __init__(self, storage: DjangoStorage):
        """
        Initialize a Django Storage instance with given options.

        :param storage: DjangoStorage class
        """
        self.storage = storage
        self.name = type(self.storage).__name__

    def __str__(self):
        return f"syncenv-{self.storage.__str__()}"

    def delete_file(self, filepath):
        self.logger.debug("Deleting file %s", filepath)
        self.storage.delete(name=filepath)

    def list_directory(self, path=""):
        return self.storage.listdir(path)[1]

    def write_file(self, filehandle, filename):
        self.logger.info(f"Writing {filename} to {self.storage.__str__()}")
        self.storage.save(name=filename, content=filehandle)
        self.logger.info(f"Completed")

    def read_file(self, filepath):
        self.logger.info("Reading file %s", filepath)
        file_ = self.storage.open(name=filepath, mode="rb")
        if not getattr(file_, "name", None):
            file_.name = filepath
        return file_

    def list_backups(
            self,
            encrypted=None,
            compressed=None,
            content_type=None,
            database=None,
            environment=None,
    ):
        """
        List stored files except given filter. If filter is None, it won't be
        used. ``content_type`` must be ``'db'`` for database backups or
        ``'media'`` for media backups.

        :param encrypted: Filter by encrypted or not
        :type encrypted: ``bool`` or ``None``

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :param environment: Filter by source environment name
        :type: ``str`` or ``None``

        :returns: List of files
        :rtype: ``list`` of ``str``
        """
        if content_type not in ("db", "media", None):
            msg = "Bad content_type %s, must be 'db', 'media', or None" % (content_type)
            raise TypeError(msg)
        # TODO: Make better filter for include only backups
        files = [f for f in self.list_directory() if utils.filename_to_datestring(f)]
        if encrypted is not None:
            files = [f for f in files if (".gpg" in f) == encrypted]
        if compressed is not None:
            files = [f for f in files if (".gz" in f) == compressed]
        if content_type == "media":
            files = [f for f in files if ".tar" in f]
        elif content_type == "db":
            files = [f for f in files if ".tar" not in f]
        if database:
            files = [f for f in files if database in f]
        if environment:
            files = [f for f in files if environment in f]
        return files

    def get_latest_backup(
            self,
            compressed=None,
            content_type=None,
            database=None,
            environment=None,
    ):
        """
        Return the latest backup file name.

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :param environment: Filter by environment name
        :type: ``str`` or ``None``

        :returns: Most recent file
        :rtype: ``str``

        :raises: FileNotFound: If no backup file is found
        """
        files = self.list_backups(
            compressed=compressed,
            content_type=content_type,
            database=database,
            environment=environment,
        )
        if not files:
            raise FileNotFound("There's no backup file available.")
        return max(files, key=utils.filename_to_date)

    def get_older_backup(
            self,
            compressed=None,
            content_type=None,
            database=None,
            environment=None,
    ):
        """
        Return the older backup's file name.

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :param environment: Filter by source environment name
        :type: ``str`` or ``None``

        :returns: Older file
        :rtype: ``str``

        :raises: FileNotFound: If no backup file is found
        """
        files = self.list_backups(
            compressed=compressed,
            content_type=content_type,
            database=database,
            environment=environment,
        )
        if not files:
            raise FileNotFound("There's no backup file available.")
        return min(files, key=utils.filename_to_date)

    def clean_old_backups(
            self,
            compressed=None,
            content_type=None,
            database=None,
            environment=None,
            keep_number=None,
    ):
        """
        Delete older backups and hold the number defined.

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :param environment: Filter by source environment name
        :type: ``str`` or ``None``

        :param keep_number: Number of files to keep, other will be deleted
        :type keep_number: ``int`` or ``None``
        """
        print(f'[DEBUGGING]: clean_old_backups::self: {self}')
        import pdb; pdb.set_trace()
        if keep_number is None:
            keep_number = (
                settings.CLEANUP_KEEP
                if content_type == "db"
                else settings.CLEANUP_KEEP_MEDIA
            )
        keep_filter = settings.CLEANUP_KEEP_FILTER
        files = self.list_backups(
            compressed=compressed,
            content_type=content_type,
            database=database,
            environment=environment,
        )

        files = sorted(files, key=utils.filename_to_date, reverse=True)
        files_to_delete = [fi for i, fi in enumerate(files) if i >= keep_number]
        for filename in files_to_delete:
            if keep_filter(filename):
                continue
            print(f'[DEBUGGING]: Deleting file {filename}')
            # self.delete_file(filename)
