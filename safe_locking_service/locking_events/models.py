from decimal import Decimal
from typing import Dict, List, Optional, TypedDict

from django.db import connection, models
from django.db.backends.utils import CursorWrapper
from django.db.models import Index, Q

from eth_typing import ChecksumAddress
from hexbytes import HexBytes
from web3.types import EventData

from gnosis.eth.django.models import (
    EthereumAddressV2Field,
    Keccak256Field,
    Uint32Field,
    Uint96Field,
)


class LeaderBoardRow(TypedDict):
    position: int
    holder: ChecksumAddress
    lockedAmount: Decimal
    unlockedAmount: Decimal
    withdrawnAmount: Decimal


def fetch_all_from_cursor(cursor: CursorWrapper) -> List[LeaderBoardRow]:
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.

    :param cursor:
    :return: all rows from a cursor as a dict.
    """
    columns = [col[0] for col in cursor.description]

    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class EthereumTxManager(models.Manager):
    """
    It is necessary to configure EthereumTxQuerySet
    """

    pass


class EthereumTxQuerySet(models.QuerySet):
    def not_confirmed(self):
        """

        :return: Block not confirmed
        """
        queryset = self.filter(confirmed=False)
        return queryset

    def since_block(self, block_number: int):
        return self.filter(block_number__gte=block_number)

    def until_block(self, block_number: int):
        return self.filter(block_number__lte=block_number)


class EthereumTx(models.Model):
    objects = EthereumTxManager.from_queryset(EthereumTxQuerySet)()
    tx_hash = Keccak256Field(primary_key=True)
    block_hash = Keccak256Field()
    block_number = Uint32Field()
    block_timestamp = models.DateTimeField()
    confirmed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            # Index to quick search sorted not confirmed blocks
            Index(
                name="Not_confirmed_block_idx",
                fields=["block_number"],
                condition=Q(confirmed=False),
            ),
        ]

    def __str__(self):
        return f"Transaction hash {self.tx_hash}"

    @staticmethod
    def create_from_decoded_event(decoded_event: EventData, block_timestamp):
        return EthereumTx.objects.get_or_create(
            tx_hash=decoded_event["transactionHash"],
            block_hash=decoded_event["blockHash"],
            block_number=decoded_event["blockNumber"],
            block_timestamp=block_timestamp,
        )


class CommonEvent(models.Model):
    """
    Abstract model that defines generic fields of a locking event. (Abstract model doesn't create tables)
    The timestamp is stored also in this model to improve the query performance.
    """

    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    ethereum_tx = models.ForeignKey(EthereumTx, on_delete=models.CASCADE)
    log_index = Uint32Field()
    holder = EthereumAddressV2Field()
    amount = Uint96Field()

    def get_serialized_timestamp(self) -> str:
        """

        :return: serialized timestamp
        """
        return self.timestamp.isoformat().replace("+00:00", "Z")

    class Meta:
        abstract = True
        indexes = [
            Index(
                fields=["holder", "-timestamp"],
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["ethereum_tx", "log_index"], name="unique_ethereum_tx_log_index"
            )
        ]

    def __str__(self):
        return f"timestamp={self.timestamp} tx-hash={self.ethereum_tx_id} log_index={self.log_index} holder={self.holder} amount={self.amount}"


class LockEvent(CommonEvent):
    """
    Model to store event Locked(address indexed holder, uint96 amount)
    """

    pass

    def __str__(self):
        return "LockEvent: " + super().__str__()

    @classmethod
    def create_instance_from_decoded_event(
        cls, decoded_event: EventData, ethereum_tx, block_timestamp
    ):
        return cls(
            timestamp=block_timestamp,
            ethereum_tx=ethereum_tx,
            log_index=decoded_event["logIndex"],
            holder=decoded_event["args"]["holder"],
            amount=decoded_event["args"]["amount"],
        )


class UnlockEvent(CommonEvent):
    """
    Model to store event Unlocked(address indexed holder, uint32 indexed index, uint96 amount)
    """

    unlock_index = Uint32Field()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["holder", "unlock_index"], name="unique_unlock_event_index"
            )
        ]

    def __str__(self):
        return "UnlockEvent: " + super().__str__()

    @classmethod
    def create_instance_from_decoded_event(
        cls, decoded_event: EventData, ethereum_tx, block_timestamp
    ):
        return cls(
            timestamp=block_timestamp,
            ethereum_tx=ethereum_tx,
            log_index=decoded_event["logIndex"],
            holder=decoded_event["args"]["holder"],
            amount=decoded_event["args"]["amount"],
            unlock_index=decoded_event["args"]["index"],
        )


class WithdrawnEvent(CommonEvent):
    """
    Model to store event Withdrawn(address indexed holder, uint32 indexed index, uint96 amount)
    """

    unlock_index = Uint32Field()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["holder", "unlock_index"], name="unique_withdrawn_event_index"
            )
        ]

    def __str__(self):
        return "WithdrawnEvent: " + super().__str__()

    @classmethod
    def create_instance_from_decoded_event(
        cls, decoded_event: EventData, ethereum_tx, block_timestamp
    ):
        return cls(
            timestamp=block_timestamp,
            ethereum_tx=ethereum_tx,
            log_index=decoded_event["logIndex"],
            holder=decoded_event["args"]["holder"],
            amount=decoded_event["args"]["amount"],
            unlock_index=decoded_event["args"]["index"],
        )


class StatusEventsIndexer(models.Model):
    contract = EthereumAddressV2Field(primary_key=True, unique=True)
    deployed_block = models.PositiveIntegerField()
    last_indexed_block = models.PositiveIntegerField()

    def __str__(self):
        return f"EventIndexer: address={self.contract} deployed_block={self.deployed_block} last_indexed_block={self.last_indexed_block} "


class LeaderBoard:
    """
    Class to group all the database queries related with leaderboard
    """

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
            return fetch_all_from_cursor(cursor)

    @classmethod
    def get_holder_position(cls, holder: ChecksumAddress) -> Optional[Dict]:
        """
        Get a holder data and position from the leaderboard ordered by lockedAmount

        :return:
        """
        query = (
            f"SELECT * from ({cls._get_leader_board_query()}) AS TEMP WHERE holder=%s"
        )
        with connection.cursor() as cursor:
            holder_address = HexBytes(holder)
            cursor.execute(query, [holder_address])
            if result := fetch_all_from_cursor(cursor):
                return result[0]

    @staticmethod
    def get_count() -> int:
        """
        Return the leaderboard size

        :return:
        """
        # LeaderBoard length should be equals than the number of holders of LockEvents
        return LockEvent.objects.values("holder").distinct().count()
