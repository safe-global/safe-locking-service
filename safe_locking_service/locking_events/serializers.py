from rest_framework import serializers

from gnosis.eth.django.serializers import EthereumAddressField, Uint32Field, Uint96Field

from safe_locking_service.locking_events.models import CommonEvent
from safe_locking_service.locking_events.services.locking_service import EventType


class CommonEventSerializer(serializers.Serializer):
    event_type = serializers.SerializerMethodField()
    execution_date = serializers.SerializerMethodField()
    transaction_hash = serializers.SerializerMethodField()
    holder = EthereumAddressField()
    amount = Uint96Field()
    log_index = Uint32Field()

    def get_event_type(self, obj: CommonEvent):
        return EventType(obj.event_type).name

    def get_execution_date(self, obj: CommonEvent):
        return obj.timestamp

    def get_transaction_hash(self, obj: CommonEvent):
        return obj.ethereum_tx_id


class LockEventSerializer(CommonEventSerializer):
    pass


class UnlockOrWitdrawEventSerializer(CommonEventSerializer):
    unlock_index = Uint32Field()


def serialize_all_events(models):
    results = []
    for model in models:
        model_type = model.event_type
        if model_type == EventType.LOCKED.value:
            serializer = LockEventSerializer
        elif (
            model_type == EventType.UNLOCKED.value
            or model_type == EventType.WITHDRAWN.value
        ):
            serializer = UnlockOrWitdrawEventSerializer
        else:
            raise ValueError(f"Type={model_type} not expected, cannot serialize")

        serialized = serializer(model)
        results.append(serialized.data)
    return results
