from django.utils import timezone

from eth_account import Account
from factory import LazyFunction, Sequence, SubFactory, fuzzy
from factory.django import DjangoModelFactory
from web3 import Web3

from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)


class EthereumTxFactory(DjangoModelFactory):
    class Meta:
        model = EthereumTx

    tx_hash = Sequence(lambda n: Web3.keccak(text=f"tx_hash-{n}").hex())
    block_hash = Sequence(lambda n: Web3.keccak(text=f"tx_hash-{n}").hex())
    block_number = Sequence(lambda n: n + 1)
    block_timestamp = LazyFunction(timezone.now)


class LockEventFactory(DjangoModelFactory):
    class Meta:
        model = LockEvent

    holder = LazyFunction(lambda: Account.create().address)
    ethereum_tx = SubFactory(EthereumTxFactory)
    amount = fuzzy.FuzzyInteger(0, 1000)
    log_index = Sequence(lambda n: n)
    block_timestamp = LazyFunction(timezone.now)


class UnlockEventFactory(DjangoModelFactory):
    class Meta:
        model = UnlockEvent

    holder = LazyFunction(lambda: Account.create().address)
    ethereum_tx = SubFactory(EthereumTxFactory)
    unlock_index = Sequence(lambda n: n + 1)
    amount = fuzzy.FuzzyInteger(0, 1000)
    log_index = Sequence(lambda n: n)
    block_timestamp = LazyFunction(timezone.now)


class WithdrawnEventFactory(DjangoModelFactory):
    class Meta:
        model = WithdrawnEvent

    holder = LazyFunction(lambda: Account.create().address)
    ethereum_tx = SubFactory(EthereumTxFactory)
    unlock_index = SubFactory(UnlockEventFactory)
    amount = fuzzy.FuzzyInteger(0, 1000)
    log_index = Sequence(lambda n: n)
    block_timestamp = LazyFunction(timezone.now)
