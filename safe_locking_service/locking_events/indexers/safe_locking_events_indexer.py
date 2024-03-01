import datetime
from logging import getLogger
from typing import List

from django.conf import settings

from web3.contract.contract import ContractEvent
from web3.types import EventData

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


class SafeLockingEventsIndexer(EventsContractIndexer):
    def __init__(self):
        self.contract_address = settings.SAFE_LOCKING_CONTRACT_ADDRESS
        super().__init__()

    @property
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
            if event["event"] in "Locked":
                LockEvent().create_from_decoded_event(
                    event, ethereum_tx, block_timestamp
                )
            elif event["event"] in "Unlocked":
                UnlockEvent().create_from_decoded_event(
                    event, ethereum_tx, block_timestamp
                )
            elif event["event"] in "Withdrawn":
                WithdrawnEvent().create_from_decoded_event(
                    event, ethereum_tx, block_timestamp
                )
            else:
                logger.ERROR(
                    "%s: Unrecognized event type: %s",
                    self.__class__.__name__,
                    event["event"],
                )
