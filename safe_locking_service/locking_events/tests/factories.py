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
    confirmed = False


class LockEventFactory(DjangoModelFactory):
    class Meta:
        model = LockEvent

    timestamp = LazyFunction(timezone.now)
    ethereum_tx = SubFactory(EthereumTxFactory)
    log_index = Sequence(lambda n: n)
    amount = fuzzy.FuzzyInteger(0, 1000)
    holder = LazyFunction(lambda: Account.create().address)


class UnlockEventFactory(DjangoModelFactory):
    class Meta:
        model = UnlockEvent

    timestamp = LazyFunction(timezone.now)
    ethereum_tx = SubFactory(EthereumTxFactory)
    log_index = Sequence(lambda n: n)
    holder = LazyFunction(lambda: Account.create().address)
    amount = fuzzy.FuzzyInteger(0, 1000)
    unlock_index = Sequence(lambda n: n + 1)


class WithdrawnEventFactory(DjangoModelFactory):
    class Meta:
        model = WithdrawnEvent

    timestamp = LazyFunction(timezone.now)
    ethereum_tx = SubFactory(EthereumTxFactory)
    log_index = Sequence(lambda n: n)
    holder = LazyFunction(lambda: Account.create().address)
    amount = fuzzy.FuzzyInteger(0, 1000)
    unlock_index = Sequence(lambda n: n + 1)
