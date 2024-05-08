from enum import Enum

from django.db.models import IntegerField, Value

from eth_typing import ChecksumAddress

from safe_locking_service.locking_events.models import (
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)


class EventType(Enum):
    LOCKED = 0
    UNLOCKED = 1
    WITHDRAWN = 2


class LockingService:
    def __init__(self, holder: ChecksumAddress):
        self.holder = holder

    def get_all_events_by_holder(self):
        """
        Get the all locking contract events by holder

        :param holder:
        :return:
        """
        # Set field unlock_index to Null to be able to apply SQL union
        # Add event_type to correctly serialize later
        lock_events = LockEvent.objects.filter(holder=self.holder).annotate(
            unlock_index=Value(None, output_field=IntegerField()),
            event_type=Value(EventType.LOCKED.value, output_field=IntegerField()),
        )

        unlock_events = UnlockEvent.objects.filter(holder=self.holder).annotate(
            event_type=Value(EventType.UNLOCKED.value, output_field=IntegerField())
        )

        withdrawn_events = WithdrawnEvent.objects.filter(holder=self.holder).annotate(
            event_type=Value(EventType.WITHDRAWN.value, output_field=IntegerField())
        )

        return (
            lock_events.union(unlock_events, all=True)
            .union(withdrawn_events, all=True)
            .order_by("-timestamp")
        )
