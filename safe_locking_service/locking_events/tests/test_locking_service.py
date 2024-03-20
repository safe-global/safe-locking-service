from django.test import TestCase

from eth_account import Account
from hexbytes import HexBytes

from ..services.locking_service import (
    EventType,
    LockingService,
)
from .utils import add_sorted_events


class TestLockingService(TestCase):
    def test_get_all_events_by_holder(self):
        address = Account.create().address
        locking_service = LockingService(address)
        self.assertEqual(len(locking_service.get_all_events_by_holder()), 0)
        add_sorted_events(address, 1000, 1000, 1000)
        all_events = locking_service.get_all_events_by_holder()
        self.assertEqual(len(all_events), 3)
        self.assertEqual(all_events[0].event_type, EventType.WITHDRAWN.value)
        self.assertEqual(all_events[1].event_type, EventType.UNLOCKED.value)
        self.assertEqual(all_events[2].event_type, EventType.LOCKED.value)
        for event in all_events:
            self.assertEqual(event.holder, address)
            self.assertEqual(event.amount, 1000)

    def test_get_leader_board(self):
        self.assertEqual(len(LockingService.get_leader_board()), 0)
        address = Account.create().address
        add_sorted_events(address, 1000, 1000, 1000)
        leader_board = LockingService.get_leader_board()
        self.assertEqual(len(leader_board), 1)
        self.assertEqual(HexBytes(leader_board[0]["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board[0]["position"], 1)
        self.assertEqual(leader_board[0]["lockedAmount"], 0)
        self.assertEqual(leader_board[0]["unlockedAmount"], 1000)
        self.assertEqual(leader_board[0]["withdrawnAmount"], 1000)
        address_2 = Account.create().address
        add_sorted_events(address_2, 2000, 1000, 1000)
        leader_board = LockingService.get_leader_board()
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
        locking_service = LockingService(address)
        self.assertIsNone(locking_service.get_leader_board_position())
        add_sorted_events(address, 1000, 1000, 1000)
        leader_board = locking_service.get_leader_board_position()
        self.assertEqual(HexBytes(leader_board["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board["position"], 1)
        self.assertEqual(leader_board["lockedAmount"], 0)
        self.assertEqual(leader_board["unlockedAmount"], 1000)
        self.assertEqual(leader_board["withdrawnAmount"], 1000)
        address_2 = Account.create().address
        add_sorted_events(address_2, 10000, 1000, 1000)
        leader_board = locking_service.get_leader_board_position()
        self.assertEqual(HexBytes(leader_board["holder"].hex()), HexBytes(address))
        self.assertEqual(leader_board["position"], 2)
        self.assertEqual(leader_board["lockedAmount"], 0)
        self.assertEqual(leader_board["unlockedAmount"], 1000)
        self.assertEqual(leader_board["withdrawnAmount"], 1000)

    def test_get_leader_board_count(self):
        self.assertEqual(LockingService.get_leader_board_count(), 0)
        address = Account.create().address
        add_sorted_events(address, 1000, 1000, 1000)
        self.assertEqual(LockingService.get_leader_board_count(), 1)
        add_sorted_events(address, 1000, 1000, 1000)
        self.assertEqual(LockingService.get_leader_board_count(), 1)
        address_2 = Account.create().address
        add_sorted_events(address_2, 1000, 1000, 1000)
        self.assertEqual(LockingService.get_leader_board_count(), 2)
