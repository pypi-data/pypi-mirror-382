import logging
from urllib.parse import quote

from .base import BaseCommandDBConnector
from .exceptions import DumpError

logger = logging.getLogger("sync_env")


def create_postgres_uri(self):
    host = self.settings.get("HOST")
    if not host:
        raise DumpError("A host name is required")

    dbname = self.settings.get("NAME") or ""
    user = quote(self.settings.get("USER") or "")
    password = self.settings.get("PASSWORD") or ""
    password = f":{quote(password)}" if password else ""
    if not user:
        password = ""
    else:
        host = "@" + host

    port = ":{}".format(self.settings.get("PORT")) if self.settings.get("PORT") else ""
    dbname = f"--dbname=postgresql://{user}{password}{host}{port}/{dbname}"
    return dbname


class PgDumpConnector(BaseCommandDBConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``psql`` for restore it.
    """

    extension = "psql"
    dump_cmd = "pg_dump"
    restore_cmd = "psql"
    single_transaction = True
    drop = True

    def _create_dump(self):
        cmd = f"{self.dump_cmd} "
        cmd = cmd + create_postgres_uri(self)

        for table in self.exclude:
            cmd += f" --exclude-table-data={table}"
        if self.drop:
            cmd += " --clean"

        cmd = f"{self.dump_prefix} {cmd} {self.dump_suffix}"
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        cmd = f"{self.restore_cmd} "
        cmd = cmd + create_postgres_uri(self)

        # without this, psql terminates with an exit value of 0 regardless of errors
        cmd += " --set ON_ERROR_STOP=on"
        if self.single_transaction:
            cmd += " --single-transaction"
        cmd += " {}".format(self.settings["NAME"])
        cmd = f"{self.restore_prefix} {cmd} {self.restore_suffix}"
        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr


class PgDumpGisConnector(PgDumpConnector):
    """
    PostgreGIS connector, same than :class:`PgDumpGisConnector` but enable
    postgis if not made.
    """

    psql_cmd = "psql"

    def _enable_postgis(self):
        cmd = f'{self.psql_cmd} -c "CREATE EXTENSION IF NOT EXISTS postgis;"'
        cmd += " --username={}".format(self.settings["ADMIN_USER"])
        cmd += " --no-password"
        if self.settings.get("HOST"):
            cmd += " --host={}".format(self.settings["HOST"])
        if self.settings.get("PORT"):
            cmd += " --port={}".format(self.settings["PORT"])
        return self.run_command(cmd)

    def _restore_dump(self, dump):
        if self.settings.get("ADMIN_USER"):
            self._enable_postgis()
        return super()._restore_dump(dump)


class PgDumpBinaryConnector(PgDumpConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``pg_restore`` for restore it.
    """

    extension = "psql.bin"
    dump_cmd = "pg_dump"
    restore_cmd = "pg_restore"
    single_transaction = True
    drop = True

    def _create_dump(self):
        cmd = f"{self.dump_cmd} "
        cmd = cmd + create_postgres_uri(self)

        cmd += " --format=custom"
        for table in self.exclude:
            cmd += f" --exclude-table-data={table}"
        cmd = f"{self.dump_prefix} {cmd} {self.dump_suffix}"
        # logger.info(cmd)
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        connection_string = create_postgres_uri(self)
        cmd = f"{self.restore_cmd} {connection_string} --clean --if-exists --no-owner"

        if self.single_transaction:
            cmd += " --single-transaction"
        if self.drop:
            cmd += ""
        cmd = f"{self.restore_prefix} {cmd} {self.restore_suffix}"

        # Drop the PUBLIC schema first
        try:
            self._drop_schema()
        except:
            logger.info("failed to drop public schema")

        try:
            self._create_schema()
        except:
            logger.info("recreate public schema")

        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr


    def _drop_schema(self, schema_name='PUBLIC', cascade=True):
        connection_string = create_postgres_uri(self)
        if cascade:
            cmd = f'psql {connection_string} -c "DROP SCHEMA {schema_name} CASCADE;"'
        else:
            cmd = f'psql {connection_string} -c "DROP SCHEMA {schema_name};"'

        cmd = f"{self.restore_prefix} {cmd} {self.restore_suffix}"
        # logger.info(cmd)
        stdout, stderr = self.run_command(cmd, env=self.restore_env)
        return stdout, stderr

    def _create_schema(self, schema_name='PUBLIC'):
        connection_string = create_postgres_uri(self)
        cmd = f'psql {connection_string} -c "CREATE SCHEMA {schema_name};"'
        cmd = f"{self.restore_prefix} {cmd} {self.restore_suffix}"
        stdout, stderr = self.run_command(cmd, env=self.restore_env)
        return stdout, stderr
