from enum import Enum
from typing import Optional

from django.db import connection
from django.db.models import IntegerField, Value

from eth_typing import ChecksumAddress
from hexbytes import HexBytes

from safe_locking_service.locking_events.models import (
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
    get_leaderboard_query,
)


class EventType(Enum):
    LOCKED = 0
    UNLOCKED = 1
    WITHDRAWN = 2


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class LockingService:
    @staticmethod
    def get_all_events(holder: ChecksumAddress):
        """
        Get the all locking contract events by holder

        :param holder:
        :return:
        """
        # Add field unlock_index to Null to be able to apply SQL union
        # Add event_type to correctly serialize later
        lock_events = LockEvent.objects.filter(holder=holder).annotate(
            unlock_index=Value(None, output_field=IntegerField()),
            event_type=Value(EventType.LOCKED.value, output_field=IntegerField()),
        )

        unlock_events = UnlockEvent.objects.filter(holder=holder).annotate(
            event_type=Value(EventType.UNLOCKED.value, output_field=IntegerField())
        )

        withdrawn_events = WithdrawnEvent.objects.filter(holder=holder).annotate(
            event_type=Value(EventType.WITHDRAWN.value, output_field=IntegerField())
        )

        return (
            lock_events.union(unlock_events, all=True)
            .union(withdrawn_events, all=True)
            .order_by("-timestamp")
        )

    @staticmethod
    def get_leader_board(holder: Optional[ChecksumAddress] = None, limit=10, offset=0):
        """
        Return leaderboard list or just LeaderBoard data for provided holder

        :return:
        """
        query = f"""
            SELECT ROW_NUMBER() OVER () AS "position",
            "holder", "total_locked" as "lockedAmount",
            "total_unlocked" as "unlockedAmount",
            "total_withdrawn" as "withdrawnAmount"
            FROM ({get_leaderboard_query()}) AS RESULT_TABLE
        """

        with connection.cursor() as cursor:
            if holder:
                query = f"SELECT * from ({query}) AS TEMP WHERE holder=%s"
                holder_address = HexBytes(holder)
                cursor.execute(query, [holder_address])
                if result := dictfetchall(cursor):
                    return result[0]
            else:
                query = f"{query} LIMIT {limit} OFFSET {offset}"
                cursor.execute(query)
                return dictfetchall(cursor)

    @staticmethod
    def get_leader_board_count():
        # TODO add a properly count less expensive
        query = f"""
            SELECT COUNT(*) FROM ({get_leaderboard_query()}) AS RESULT_TABLE
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]
