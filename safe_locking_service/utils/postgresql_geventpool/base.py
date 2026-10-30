from django_db_geventpool.backends.postgresql_psycopg2.base import (
    DatabaseWrapper as GeventpoolDatabaseWrapper,
)


class DatabaseWrapper(GeventpoolDatabaseWrapper):
    """
    Django >= 5.1 has its own psycopg pool and checks `self.pool` to know if it is in use.
    geventpool defines a `pool` property too, so Django thinks its own pool is configured:
    it does not set the time zone or role on new connections, and `close_pool` breaks
    """

    def init_connection_state(self):
        super().init_connection_state()
        if self.connection is not None:
            commit = self._configure_connection(self.connection)
            if commit and not self.get_autocommit():
                self.connection.commit()

    def close_pool(self):
        if self._pool is not None:
            self._pool.close()
            self._connection_pools.pop(self.alias, None)
            self._pool = None
