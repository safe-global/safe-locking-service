from django.test import TestCase

from eth_account import Account

from ..services.locking_service import EventType, LockingService
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
