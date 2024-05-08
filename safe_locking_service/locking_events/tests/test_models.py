from django.db import IntegrityError
from django.test import TestCase

from eth_account import Account
from hexbytes import HexBytes

from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
    get_leader_board,
    get_leader_board_count,
    get_leader_board_holder_position,
)
from safe_locking_service.locking_events.tests.factories import (
    LockEventFactory,
    UnlockEventFactory,
    WithdrawnEventFactory,
)

from .utils import add_sorted_events


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

    def test_get_leader_board(self):
        self.assertEqual(len(get_leader_board(limit=10, offset=0)), 0)
        address = Account.create().address
        add_sorted_events(address, 1000, 1000, 1000)
        leader_board = get_leader_board(limit=10, offset=0)
        self.assertEqual(len(leader_board), 1)
        self.assertEqual(HexBytes(leader_board[0]["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board[0]["position"], 1)
        self.assertEqual(leader_board[0]["lockedAmount"], 0)
        self.assertEqual(leader_board[0]["unlockedAmount"], 1000)
        self.assertEqual(leader_board[0]["withdrawnAmount"], 1000)
        address_2 = Account.create().address
        add_sorted_events(address_2, 2000, 1000, 1000)
        leader_board = get_leader_board(limit=10, offset=0)
        self.assertEqual(len(leader_board), 2)
        self.assertEqual(HexBytes(leader_board[0]["holder"].hex()), HexBytes(address_2))
        self.assertEqual(leader_board[0]["position"], 1)
        self.assertEqual(leader_board[0]["lockedAmount"], 1000)
        self.assertEqual(leader_board[0]["unlockedAmount"], 1000)
        self.assertEqual(leader_board[0]["withdrawnAmount"], 1000)
        self.assertEqual(HexBytes(leader_board[1]["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board[1]["position"], 2)
        self.assertEqual(leader_board[1]["lockedAmount"], 0)
        self.assertEqual(leader_board[1]["unlockedAmount"], 1000)
        self.assertEqual(leader_board[1]["withdrawnAmount"], 1000)

    def test_get_leader_board_position(self):
        address = Account.create().address
        self.assertIsNone(get_leader_board_holder_position(address))
        add_sorted_events(address, 1000, 1000, 1000)
        leader_board = get_leader_board_holder_position(address)
        self.assertEqual(HexBytes(leader_board["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board["position"], 1)
        self.assertEqual(leader_board["lockedAmount"], 0)
        self.assertEqual(leader_board["unlockedAmount"], 1000)
        self.assertEqual(leader_board["withdrawnAmount"], 1000)
        address_2 = Account.create().address
        add_sorted_events(address_2, 10000, 1000, 1000)
        leader_board = get_leader_board_holder_position(address)
        self.assertEqual(HexBytes(leader_board["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board["position"], 2)
        self.assertEqual(leader_board["lockedAmount"], 0)
        self.assertEqual(leader_board["unlockedAmount"], 1000)
        self.assertEqual(leader_board["withdrawnAmount"], 1000)

    def test_get_leader_board_count(self):
        self.assertEqual(get_leader_board_count(), 0)
        address = Account.create().address
        add_sorted_events(address, 1000, 1000, 1000)
        self.assertEqual(get_leader_board_count(), 1)
        add_sorted_events(address, 1000, 1000, 1000)
        self.assertEqual(get_leader_board_count(), 1)
        address_2 = Account.create().address
        add_sorted_events(address_2, 1000, 1000, 1000)
        self.assertEqual(get_leader_board_count(), 2)
