from django.db.models import Sum
from django.test import TestCase

from gnosis.eth.tests.ethereum_test_case import EthereumTestCaseMixin

from ..contracts.locking_contract import deploy_locking_contract
from ..indexers.safe_locking_events_indexer import (
    SafeLockingEventsIndexer,
    get_safe_locking_event_indexer,
)
from ..models import (
    EthereumTx,
    LockEvent,
    StatusEventsIndexer,
    UnlockEvent,
    WithdrawnEvent,
)
from .mocks.mocks_locking_events_indexer import (
    invalid_key_event,
    invalid_lock_event,
    invalid_unlock_event,
    invalid_withdrawn_event,
    valid_lock_event,
    valid_unlock_event,
    valid_withdrawn_event,
)
from .utils import (
    erc20_approve,
    increment_chain_time,
    locking_contract_lock,
    locking_contract_unlock,
    locking_contract_withdraw,
)


class TestLockingEventsIndexer(EthereumTestCaseMixin, TestCase):
    cooldown_period = 2

    def setUp(self) -> None:
        account = self.ethereum_test_account
        amount = 10000000
        self.erc20_contract = self.deploy_example_erc20(amount, account.address)
        self.locking_contract = deploy_locking_contract(
            self.ethereum_client,
            account,
            self.erc20_contract.address,
            self.cooldown_period,
        )
        self.locking_contract_address = self.locking_contract.address
        self.assertIsNotNone(self.locking_contract.address)
        StatusEventsIndexer.objects.create(
            contract=self.locking_contract_address,
            deployed_block=0,
            last_indexed_block=0,
        )

    def test_get_safe_locking_event_indexer(self):
        with self.settings(SAFE_LOCKING_CONTRACT_ADDRESS=self.locking_contract_address):
            locking_events_indexer = get_safe_locking_event_indexer()
            self.assertEqual(
                locking_events_indexer.contract_address, self.locking_contract_address
            )
            self.assertEqual(locking_events_indexer, get_safe_locking_event_indexer())

    def test_index_lock_events(self):
        account = self.ethereum_test_account
        lock_amount = 100
        erc20_approve(
            self.ethereum_client.w3,
            account,
            self.erc20_contract,
            self.locking_contract.address,
            lock_amount,
        )
        locking_events_indexer = SafeLockingEventsIndexer(self.locking_contract_address)
        locking_events_indexer.index_until_last_chain_block()
        self.assertEqual(EthereumTx.objects.count(), 0)
        self.assertEqual(LockEvent.objects.count(), 0)
        for i in range(0, 10):
            locking_contract_lock(
                self.ethereum_client.w3, account, self.locking_contract, 10
            )

        locking_events_indexer.index_until_last_chain_block()
        self.assertEqual(EthereumTx.objects.count(), 10)
        self.assertEqual(LockEvent.objects.filter(holder=account.address).count(), 10)
        self.assertEqual(
            LockEvent.objects.filter(holder=account.address).aggregate(
                total=Sum("amount")
            )["total"],
            100,
        )

    def test_index_unlock_events(self):
        account = self.ethereum_test_account
        lock_amount = 100
        erc20_approve(
            self.ethereum_client.w3,
            account,
            self.erc20_contract,
            self.locking_contract.address,
            lock_amount,
        )
        locking_events_indexer = SafeLockingEventsIndexer(self.locking_contract_address)
        locking_events_indexer.index_until_last_chain_block()
        self.assertEqual(EthereumTx.objects.count(), 0)
        self.assertEqual(UnlockEvent.objects.count(), 0)
        locking_contract_lock(
            self.ethereum_client.w3, account, self.locking_contract, 100
        )
        for i in range(0, 10):
            locking_contract_unlock(
                self.ethereum_client.w3, account, self.locking_contract, 10
            )
        locking_events_indexer.index_until_last_chain_block()
        # 1 Lock and 10 Unlock
        self.assertEqual(EthereumTx.objects.count(), 11)
        self.assertEqual(LockEvent.objects.filter(holder=account.address).count(), 1)
        self.assertEqual(UnlockEvent.objects.filter(holder=account.address).count(), 10)
        self.assertEqual(
            UnlockEvent.objects.filter(holder=account.address).aggregate(
                total=Sum("amount")
            )["total"],
            100,
        )

    def test_index_withdrawn_events(self):
        account = self.ethereum_test_account
        lock_amount = 100
        erc20_approve(
            self.ethereum_client.w3,
            account,
            self.erc20_contract,
            self.locking_contract.address,
            lock_amount,
        )
        locking_events_indexer = SafeLockingEventsIndexer(self.locking_contract_address)
        locking_events_indexer.index_until_last_chain_block()
        self.assertEqual(EthereumTx.objects.count(), 0)
        self.assertEqual(UnlockEvent.objects.count(), 0)
        locking_contract_lock(
            self.ethereum_client.w3, account, self.locking_contract, 100
        )
        for i in range(0, 10):
            locking_contract_unlock(
                self.ethereum_client.w3, account, self.locking_contract, 10
            )
        locking_events_indexer.index_until_last_chain_block()
        increment_chain_time(self.ethereum_client.w3, self.cooldown_period)
        locking_contract_withdraw(
            self.ethereum_client.w3, account, self.locking_contract, 5
        )
        locking_events_indexer.index_until_last_chain_block()
        # 1 Lock, 10 Unlock and 1 Withdrawn
        self.assertEqual(EthereumTx.objects.count(), 12)
        self.assertEqual(LockEvent.objects.filter(holder=account.address).count(), 1)
        self.assertEqual(UnlockEvent.objects.filter(holder=account.address).count(), 10)
        # 5 withdrawn with amount of 10 by previous unlock event.
        self.assertEqual(
            WithdrawnEvent.objects.filter(holder=account.address).count(), 5
        )

        self.assertEqual(
            WithdrawnEvent.objects.filter(holder=account.address).aggregate(
                total=Sum("amount")
            )["total"],
            50,
        )

    def test_event_decoding(self):
        locking_events_indexer = SafeLockingEventsIndexer(self.locking_contract_address)

        self.assertRaises(
            KeyError, locking_events_indexer.decode_event, invalid_key_event
        )

        data_lock_event = locking_events_indexer.decode_event(valid_lock_event)
        self.assertEqual(data_lock_event.get("event"), "Locked")
        self.assertEqual(
            data_lock_event.get("args").get("holder"),
            "0x22D491bde2303f2F43325b2108d26F1EaBA1E32A",
        )
        self.assertEqual(data_lock_event.get("args").get("amount"), 100)

        invalid_data_lock_event = locking_events_indexer.decode_event(
            invalid_lock_event
        )
        self.assertIsNone(invalid_data_lock_event)

        data_unlock_event = locking_events_indexer.decode_event(valid_unlock_event)
        self.assertEqual(data_unlock_event.get("event"), "Unlocked")
        self.assertEqual(
            data_unlock_event.get("args").get("holder"),
            "0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b",
        )
        self.assertEqual(data_unlock_event.get("args").get("index"), 9)
        self.assertEqual(data_unlock_event.get("args").get("amount"), 10)

        invalid_data_unlock_event = locking_events_indexer.decode_event(
            invalid_unlock_event
        )
        self.assertIsNone(invalid_data_unlock_event)

        data_withdrawn_event = locking_events_indexer.decode_event(
            valid_withdrawn_event
        )
        self.assertEqual(data_withdrawn_event.get("event"), "Withdrawn")
        self.assertEqual(
            data_withdrawn_event.get("args").get("holder"),
            "0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b",
        )
        self.assertEqual(data_withdrawn_event.get("args").get("index"), 2)
        self.assertEqual(data_withdrawn_event.get("args").get("amount"), 10)

        invalid_data_withdrawn_event = locking_events_indexer.decode_event(
            invalid_withdrawn_event
        )
        self.assertIsNone(invalid_data_withdrawn_event)
