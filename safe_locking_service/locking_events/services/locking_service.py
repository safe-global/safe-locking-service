from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, TypedDict

from django.db import connection
from django.db.backends.utils import CursorWrapper
from django.db.models import IntegerField, Value

from eth_typing import ChecksumAddress
from hexbytes import HexBytes

from safe_locking_service.locking_events.models import (
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)


class LeaderBoardRow(TypedDict):
    position: int
    holder: ChecksumAddress
    lockedAmount: Decimal
    unlockedAmount: Decimal
    withdrawnAmount: Decimal


class EventType(Enum):
    LOCKED = 0
    UNLOCKED = 1
    WITHDRAWN = 2


def fetch_all_from_cursor(cursor: CursorWrapper) -> List[LeaderBoardRow]:
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.

    :param cursor:
    :return: all rows from a cursor as a dict.
    """
    columns = [col[0] for col in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class LockingService:
    def __init__(self, holder: ChecksumAddress):
        self.holder = holder

    def get_all_events_by_holder(self):
        """
        Get the all locking contract events by holder

        :param holder:
        :return:
        """
        # Set field unlock_index to Null to be able to apply SQL union
        # Add event_type to correctly serialize later
        lock_events = LockEvent.objects.filter(holder=self.holder).annotate(
            unlock_index=Value(None, output_field=IntegerField()),
            event_type=Value(EventType.LOCKED.value, output_field=IntegerField()),
        )

        unlock_events = UnlockEvent.objects.filter(holder=self.holder).annotate(
            event_type=Value(EventType.UNLOCKED.value, output_field=IntegerField())
        )

        withdrawn_events = WithdrawnEvent.objects.filter(holder=self.holder).annotate(
            event_type=Value(EventType.WITHDRAWN.value, output_field=IntegerField())
        )

        return (
            lock_events.union(unlock_events, all=True)
            .union(withdrawn_events, all=True)
            .order_by("-timestamp")
        )

    @classmethod
    def _get_leader_board_query(cls) -> str:
        """
        Get raw leaderboard SQL query

        :return:
        """
        union_lock_unlock_withdraw_events = """
                        (SELECT "locking_events_lockevent"."holder" AS "holder",
                               "locking_events_lockevent"."amount" AS "amount",
                                0 AS "event_type"
                        FROM "locking_events_lockevent"
                        ) UNION ALL (
                        SELECT "locking_events_unlockevent"."holder" AS "holder",
                               "locking_events_unlockevent"."amount" AS "amount",
                                1 AS "event_type"
                        FROM "locking_events_unlockevent")
                        UNION ALL
                        (SELECT "locking_events_withdrawnevent"."holder" AS "holder",
                                "locking_events_withdrawnevent"."amount" AS "amount",
                                2 AS "event_type"
                        FROM "locking_events_withdrawnevent")
                        """

        total_lock_unlock_withdraw_amount = f"""
                        SELECT "holder", SUM(COALESCE(CASE WHEN "event_type" = 0 THEN "amount" ELSE NULL END,
                                CASE WHEN "event_type" = 1 THEN -amount ELSE NULL END)) AS "lockedAmount",
                                SUM(CASE WHEN "event_type" = 1 THEN "amount" ELSE 0 END) AS "unlockedAmount",
                                SUM(CASE WHEN "event_type" = 2 THEN "amount" ELSE 0 END) AS "withdrawnAmount"
                        FROM (
                            {union_lock_unlock_withdraw_events}
                        ) AS "UNION_TABLE"
                        GROUP BY "holder" ORDER BY "lockedAmount" DESC
                        """

        leader_board_query = f"""
                        SELECT ROW_NUMBER() OVER () AS "position",
                        *
                        FROM ({total_lock_unlock_withdraw_amount}) AS RESULT_TABLE
                """
        return leader_board_query

    @classmethod
    def get_leader_board(cls, limit: int, offset: int) -> List[Dict]:
        """
        Return the leaderboard list ordered by lockedAmount

        :return:
        """
        query = f"{cls._get_leader_board_query()} LIMIT {limit} OFFSET {offset}"
        with connection.cursor() as cursor:
            cursor.execute(query)
            return fectch_all_from_cursor(cursor)

    def get_leader_board_position(self) -> Optional[Dict]:
        """
        Get a holder data from the leaderboard

        :return:
        """
        query = (
            f"SELECT * from ({self._get_leader_board_query()}) AS TEMP WHERE holder=%s"
        )
        with connection.cursor() as cursor:
            holder_address = HexBytes(self.holder)
            cursor.execute(query, [holder_address])
            if result := fectch_all_from_cursor(cursor):
                return result[0]

    @staticmethod
    def get_leader_board_count() -> int:
        """
        Return the leaderboard size

        :return:
        """
        # LeaderBoard length should be equals than the number of holders of LockEvents
        return LockEvent.objects.values("holder").distinct().count()
