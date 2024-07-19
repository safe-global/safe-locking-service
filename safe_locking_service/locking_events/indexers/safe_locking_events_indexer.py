import datetime
from functools import cache, cached_property
from logging import getLogger
from typing import List

from django.conf import settings

from eth_typing import ChecksumAddress
from web3.contract.contract import ContractEvent
from web3.types import EventData

from gnosis.eth.ethereum_client import get_auto_ethereum_client

from safe_locking_service.locking_events.contracts.locking_contract import (
    get_locking_contract,
)
from safe_locking_service.locking_events.indexers.events_indexer import (
    EventsContractIndexer,
)
from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)

logger = getLogger(__name__)


@cache
def get_safe_locking_event_indexer():
    """
    Return singleton instance of SafeLockingEventsIndexer

    :return:
    """
    return SafeLockingEventsIndexer(settings.SAFE_LOCKING_CONTRACT_ADDRESS)


class SafeLockingEventsIndexer(EventsContractIndexer):
    def __init__(self, contract_address: ChecksumAddress, *args, **kwargs):
        self.contract_address = contract_address

        super().__init__(ethereum_client=get_auto_ethereum_client(), *args, **kwargs)

    @cached_property
    def contract_events(self) -> List[ContractEvent]:
        """
        :return: List of Web3.py `ContractEvent` to listen to
        """
        safe_locking_contract = get_locking_contract(self.ethereum_client.w3)
        return [
            safe_locking_contract.events.Locked(),
            safe_locking_contract.events.Unlocked(),
            safe_locking_contract.events.Withdrawn(),
        ]

    def process_decoded_events(self, decoded_events: List[EventData]):
        for event in decoded_events:
            block_timestamp = datetime.datetime.fromtimestamp(
                self.ethereum_client.get_block(event["blockNumber"])["timestamp"],
                datetime.timezone.utc,
            )
            ethereum_tx, created = EthereumTx().create_from_decoded_event(
                event, block_timestamp
            )
            lock_event_instances = []
            unlock_event_instances = []
            withdrawn_event_instances = []
            if event["event"] == "Locked":
                lock_event_instances.append(
                    LockEvent.create_instance_from_decoded_event(
                        event, ethereum_tx, block_timestamp
                    )
                )
            elif event["event"] == "Unlocked":
                unlock_event_instances.append(
                    UnlockEvent.create_instance_from_decoded_event(
                        event, ethereum_tx, block_timestamp
                    )
                )
            elif event["event"] == "Withdrawn":
                withdrawn_event_instances.append(
                    WithdrawnEvent.create_instance_from_decoded_event(
                        event, ethereum_tx, block_timestamp
                    )
                )
            else:
                logger.error(
                    "%s: Unrecognized event type: %s",
                    self.__class__.__name__,
                    event["event"],
                )
            LockEvent.objects.bulk_create(lock_event_instances, ignore_conflicts=True)
            UnlockEvent.objects.bulk_create(
                unlock_event_instances, ignore_conflicts=True
            )
            WithdrawnEvent.objects.bulk_create(
                withdrawn_event_instances, ignore_conflicts=True
            )
