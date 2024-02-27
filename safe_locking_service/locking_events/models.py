from django.db import models

from gnosis.eth.django.models import EthereumAddressV2Field, Keccak256Field


class EthereumTx(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tx_hash = Keccak256Field(primary_key=True)
    block_hash = Keccak256Field()
    block_number = models.PositiveIntegerField()
    block_timestamp = models.DateTimeField()

    def __str__(self):
        return f"Transaction hash {self.tx_hash}"


class CommonEvent(models.Model):
    """
    Abstract model that defines generic fields of a locking event. (Abstract model doesn't create tables)
    The block timestamp is stored also in this model to improve the query performance.
    """

    id = models.AutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    holder = EthereumAddressV2Field()
    ethereum_tx = models.ForeignKey(EthereumTx, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    log_index = models.PositiveIntegerField()
    block_timestamp = models.DateTimeField()

    class Meta:
        abstract = True


class LockEvent(CommonEvent):
    """
    Model to store event Locked(address indexed holder, uint96 amount)
    """

    pass

    def __str__(self):
        return f"Holder {self.holder} locked {self.amount} Safe tokens"


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
        return f"Holder {self.holder} unlocked {self.amount} Safe tokens"


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

    def __str__(self):
        return f"Holder {self.holder} withdrawn {self.amount} Safe tokens"
