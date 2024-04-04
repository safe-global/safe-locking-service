from typing import Dict, List, Union

from rest_framework import serializers

from gnosis.eth.django.serializers import EthereumAddressField, Uint32Field, Uint96Field
from gnosis.eth.utils import fast_to_checksum_address

from safe_locking_service.locking_events.models import (
    CommonEvent,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)
from safe_locking_service.locking_events.services.locking_service import EventType


class EventTypeSerializer(serializers.Serializer):
    event_type = serializers.SerializerMethodField()

    def get_event_type(self, obj: CommonEvent):
        return EventType(obj.event_type).name


class CommonEventSerializer(serializers.Serializer):
    execution_date = serializers.SerializerMethodField()
    transaction_hash = serializers.SerializerMethodField()
    holder = EthereumAddressField()
    amount = Uint96Field()
    log_index = Uint32Field()

    def get_execution_date(self, obj: CommonEvent):
        return obj.timestamp

    def get_transaction_hash(self, obj: CommonEvent):
        return obj.ethereum_tx_id


class LockEventSerializer(CommonEventSerializer):
    pass


class LockEventWithTypeSerializer(CommonEventSerializer, EventTypeSerializer):
    pass


class UnlockOrWitdrawnEventSerializer(CommonEventSerializer):
    unlock_index = Uint32Field()


class UnlockOrWitdrawnEventWithTypeSerializer(
    UnlockOrWitdrawnEventSerializer, EventTypeSerializer
):
    pass


class AllEventsDocSerializer(serializers.Serializer):
    """
    Just for the purpose of documenting, don't use it
    """

    lock_event = LockEventWithTypeSerializer()
    unlock_event = UnlockOrWitdrawnEventWithTypeSerializer()
    withdrawn_event = UnlockOrWitdrawnEventWithTypeSerializer()


def serialize_all_events(
    queryset: List[Union[LockEvent, UnlockEvent, WithdrawnEvent]]
) -> List[Dict]:
    """
    Return a list of serialized events from provided queryset list

    :param queryset:
    :return:
    """
    results = []
    for model in queryset:
        model_type = model.event_type
        if model_type == EventType.LOCKED.value:
            serializer = LockEventWithTypeSerializer
        elif (
            model_type == EventType.UNLOCKED.value
            or model_type == EventType.WITHDRAWN.value
        ):
            serializer = UnlockOrWitdrawnEventWithTypeSerializer
        else:
            raise ValueError(f"Type={model_type} not expected, cannot serialize")

        serialized = serializer(model)
        results.append(serialized.data)
    return results


class LeaderBoardSerializer(serializers.Serializer):
    holder = serializers.SerializerMethodField()
    position = serializers.IntegerField()
    lockedAmount = Uint96Field()
    unlockedAmount = Uint96Field()
    withdrawnAmount = Uint96Field()

    def get_holder(self, obj: Dict):
        return fast_to_checksum_address(bytes(obj["holder"]))
