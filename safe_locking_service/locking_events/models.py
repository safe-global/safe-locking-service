from django.db import models

from gnosis.eth.django.models import EthereumAddressV2Field, Keccak256Field, Uint96Field


class EthereumTx(models.Model):
    tx_hash = Keccak256Field(primary_key=True)
    block_hash = Keccak256Field()
    block_number = models.PositiveIntegerField()
    block_timestamp = models.DateTimeField()

    def __str__(self):
        return f"Transaction hash {self.tx_hash}"


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
        return f"timestamp={self.timestamp} tx-hash={self.ethereum_tx_id}  log_index={self.log_index} holder={self.holder}"


class LockEvent(CommonEvent):
    """
    Model to store event Locked(address indexed holder, uint96 amount)
    """

    pass


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


class WithdrawnEvent(CommonEvent):
    """
    Model to store event Withdrawn(address indexed holder, uint32 indexed index, uint96 amount)
    """

    unlock_index = models.ForeignKey(UnlockEvent, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["holder", "unlock_index"], name="unique_withdrawn_event_index"
            )
        ]
