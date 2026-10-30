from django.db import connection
from django.test import TestCase, override_settings

from ..postgresql_geventpool.base import DatabaseWrapper


class TestPostgresqlGeventpool(TestCase):
    def get_connection_time_zone(self, database_wrapper=connection) -> str:
        with database_wrapper.cursor() as cursor:
            cursor.execute("SHOW TIME ZONE")
            return cursor.fetchone()[0]

    def test_new_connection_time_zone(self):
        # Django must set its own time zone, not keep the one of the server
        settings_dict = {
            **connection.settings_dict,
            "OPTIONS": {
                **connection.settings_dict["OPTIONS"],
                "options": "-c timezone=Europe/Madrid",
            },
        }
        database_wrapper = DatabaseWrapper(settings_dict, alias="test_time_zone")
        try:
            self.assertEqual(self.get_connection_time_zone(database_wrapper), "UTC")
        finally:
            database_wrapper.close()
            database_wrapper.close_pool()

    def test_time_zone_setting_changed(self):
        # Changing the time zone settings closes the pool when entering and leaving the block
        with override_settings(USE_TZ=False, TIME_ZONE="Europe/Madrid"):
            self.assertEqual(self.get_connection_time_zone(), "Europe/Madrid")
        self.assertEqual(self.get_connection_time_zone(), "UTC")

    def test_close_pool(self):
        connection.close_pool()
        connection.close_pool()
        self.assertEqual(self.get_connection_time_zone(), "UTC")
