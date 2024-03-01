from django.db import models

from web3.types import EventData

from gnosis.eth.django.models import EthereumAddressV2Field, Keccak256Field, Uint96Field


class EthereumTx(models.Model):
    tx_hash = Keccak256Field(primary_key=True)
    block_hash = Keccak256Field()
    block_number = models.PositiveIntegerField()
    block_timestamp = models.DateTimeField()

    def __str__(self):
        return f"Transaction hash {self.tx_hash}"

    def create_from_decoded_event(self, decoded_event: EventData, block_timestamp):
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
    log_index = models.PositiveIntegerField()
    holder = EthereumAddressV2Field()
    amount = Uint96Field()

    class Meta:
        abstract = True
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

    unlock_index = models.PositiveIntegerField()

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

    unlock_index = models.PositiveIntegerField()

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
