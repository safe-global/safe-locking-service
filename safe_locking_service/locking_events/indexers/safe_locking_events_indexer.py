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
    FindRelevantEventsException,
)
from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
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

    def index_until_last_chain_block(self):
        """
        Function that index from last indexed block until current last block in the chain.
        This function also updates the last indexed block in database.
        """
        last_current_block = self.get_current_last_block()
        from_block = self.get_from_block(self.contract_address)
        logger.info(f"Starting indexer, pending-blocks:{last_current_block-from_block}")

        while from_block < last_current_block:
            to_block = self.get_to_block(from_block, last_current_block)
            logger.info(
                f"Indexing from-block {from_block} to-block {to_block} pending-blocks {last_current_block-to_block}"
            )
            try:
                log_receipts = self.find_relevant_events(from_block, to_block)
            except FindRelevantEventsException:
                self.reset_block_process_limit()
                continue

            if log_receipts:
                unprocessed_events = self.get_unprocessed_events(log_receipts)
                logger.info(
                    f"Processing {len(unprocessed_events)} events from {len(log_receipts)} events"
                )
                decoded_events: List[EventData] = self.decode_events(unprocessed_events)
                # TODO Refactor inserts
                locked_events = []
                unlocked_events = []
                for event in decoded_events:
                    timestamp = datetime.datetime.fromtimestamp(
                        self.ethereum_client.get_block(event["blockNumber"])[
                            "timestamp"
                        ],
                        datetime.timezone.utc,
                    )
                    ethereum_tx, created = EthereumTx.objects.get_or_create(
                        tx_hash=event["transactionHash"],
                        block_hash=event["blockHash"],
                        block_number=event["blockNumber"],
                        block_timestamp=timestamp,
                    )
                    if created:
                        if event["event"] in "Unlocked":
                            unlocked_events.append(
                                UnlockEvent(
                                    timestamp=timestamp,
                                    ethereum_tx=ethereum_tx,
                                    log_index=event["logIndex"],
                                    holder=event["args"]["holder"],
                                    amount=event["args"]["amount"],
                                    unlock_index=event["args"]["index"],
                                )
                            )
                        elif event["event"] in "Locked":
                            locked_events.append(
                                LockEvent(
                                    timestamp=timestamp,
                                    ethereum_tx=ethereum_tx,
                                    log_index=event["logIndex"],
                                    holder=event["args"]["holder"],
                                    amount=event["args"]["amount"],
                                )
                            )

                LockEvent.objects.bulk_create(locked_events)
                UnlockEvent.objects.bulk_create(unlocked_events)
                self.set_processed_events(unprocessed_events)
            # Update from block
            from_block = to_block
        # Update last block indexed
        self.set_last_indexed_block(self.contract_address, from_block)
