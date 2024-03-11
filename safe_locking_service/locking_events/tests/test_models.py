from django.db import IntegrityError
from django.test import TestCase

from eth_account import Account

from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)
from safe_locking_service.locking_events.tests.factories import (
    LockEventFactory,
    UnlockEventFactory,
    WithdrawnEventFactory,
)


class TestLockingModel(TestCase):
    def test_create_lock_event(self):
        safe_address = Account.create().address
        ethereum_tx = LockEventFactory(holder=safe_address, amount=1000).ethereum_tx
        self.assertEqual(EthereumTx.objects.count(), 1)
        lock_event = LockEvent.objects.filter(
            holder=safe_address, ethereum_tx=ethereum_tx
        )[0]
        self.assertEqual(lock_event.holder, safe_address)
        self.assertEqual(lock_event.amount, 1000)

    def test_create_unlock_event(self):
        safe_address = Account.create().address
        ethereum_tx = UnlockEventFactory(holder=safe_address, amount=1000).ethereum_tx
        self.assertEqual(EthereumTx.objects.count(), 1)
        unlock_event = UnlockEvent.objects.filter(
            holder=safe_address, ethereum_tx=ethereum_tx
        )[0]
        self.assertEqual(unlock_event.holder, safe_address)
        self.assertEqual(unlock_event.amount, 1000)
        with self.assertRaisesMessage(IntegrityError, "violates unique constraint"):
            UnlockEventFactory(
                holder=safe_address, amount=1000, unlock_index=unlock_event.unlock_index
            )

    def test_create_withdrawn_event(self):
        safe_address = Account.create().address
        ethereum_tx = WithdrawnEventFactory(
            holder=safe_address, amount=1000
        ).ethereum_tx
        # Expected at least two transactions, one for unlock and other for withdrawn
        self.assertEqual(EthereumTx.objects.count(), 1)
        withdrawn_event = WithdrawnEvent.objects.filter(
            holder=safe_address, ethereum_tx=ethereum_tx
        )[0]
        self.assertEqual(withdrawn_event.holder, safe_address)
        self.assertEqual(withdrawn_event.amount, 1000)
        with self.assertRaisesMessage(IntegrityError, "violates unique constraint"):
            WithdrawnEventFactory(
                holder=safe_address,
                amount=1000,
                unlock_index=withdrawn_event.unlock_index,
            )
