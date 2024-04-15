from abc import abstractmethod
from functools import cached_property
from logging import getLogger
from typing import Dict, List, Optional, Sequence

from eth_abi.exceptions import DecodingError
from eth_typing import ChecksumAddress
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes
from web3.contract.contract import ContractEvent
from web3.exceptions import LogTopicError
from web3.types import EventData, FilterParams, LogReceipt

from .base_indexer import BaseIndexer
from .element_already_processed_checker import ElementAlreadyProcessedChecker

logger = getLogger(__name__)


class FindRelevantEventsException(Exception):
    pass


class EventsContractIndexer(BaseIndexer):
    """
    Index contract events
    """

    contract_address: ChecksumAddress

    def __init__(self, *args, **kwargs):
        # Number of concurrent requests to `getLogs`
        self.element_already_processed_checker = ElementAlreadyProcessedChecker()
        super().__init__(*args, **kwargs)

    @cached_property
    @abstractmethod
    def contract_events(self) -> List[ContractEvent]:
        """
        :return: List of Web3.py `ContractEvent` to listen to
        """

    @cached_property
    def events_to_listen(self) -> Dict[bytes, List[ContractEvent]]:
        """
        Build a dictionary with a `topic` and a list of ABIs to use for decoding. One single topic can have
        multiple ways of decoding as events with different `indexed` parameters must be decoded
        in a different way

        :return: Dictionary with `topic` as the key and a list of `ContractEvent`
        """
        events_to_listen = {}
        for event in self.contract_events:
            key = HexBytes(event_abi_to_log_topic(event.abi)).hex()
            events_to_listen.setdefault(key, []).append(event)
        return events_to_listen

    def _fetch_log_events_from_node(
        self,
        from_block_number: int,
        to_block_number: int,
    ) -> List[LogReceipt]:
        """
        Perform query to the node

        :param from_block_number:
        :param to_block_number:
        :return:
        """
        filter_topics = list(self.events_to_listen.keys())
        parameters: FilterParams = {
            "address": self.contract_address,
            "fromBlock": from_block_number,
            "toBlock": to_block_number,
            "topics": [filter_topics],
        }
        with self.auto_adjust_block_limit(from_block_number, to_block_number):
            return self.ethereum_client.slow_w3.eth.get_logs(parameters)

    def _find_log_events_by_topics(
        self,
        from_block_number: int,
        to_block_number: int,
    ) -> List[LogReceipt]:
        """
        It will get contract events using filtering by contract_events topics.

        :param from_block_number:
        :param to_block_number:
        :return: LogReceipt for matching events
        """
        try:
            return self._fetch_log_events_from_node(from_block_number, to_block_number)
        except IOError as e:
            logger.error(
                "%s: Error retrieving events from-block=%d to-block=%d : %s",
                self.__class__.__name__,
                from_block_number,
                to_block_number,
                e,
            )
            raise FindRelevantEventsException(
                f"Request error retrieving events "
                f"from-block={from_block_number} to-block={to_block_number}"
            ) from e
        except ValueError as e:
            logger.error(
                "%s: Value error retrieving events from-block=%d to-block=%d : %s",
                self.__class__.__name__,
                from_block_number,
                to_block_number,
                e,
            )
            raise FindRelevantEventsException(
                f"Request error retrieving events "
                f"from-block={from_block_number} to-block={to_block_number}"
            ) from e

    def find_relevant_log_events(
        self,
        from_block_number: int,
        to_block_number: int,
    ) -> List[LogReceipt]:
        """
        Search for log receipts for contract events

        :param from_block_number: Starting block number
        :param to_block_number: Ending block number
        :return: LogReceipt for matching events
        """
        logger.debug(
            "%s: Filtering for events from block-number=%d to block-number=%d for locking contract %s",
            self.__class__.__name__,
            from_block_number,
            to_block_number,
            self.contract_address,
        )
        log_receipts = self._find_log_events_by_topics(
            from_block_number, to_block_number
        )

        len_log_receipts = len(log_receipts)
        logger_fn = logger.info if len_log_receipts else logger.debug
        logger_fn(
            "%s: Found %d events from block-number=%d to block-number=%d for locking contract %s addresses",
            self.__class__.__name__,
            len_log_receipts,
            from_block_number,
            to_block_number,
            self.contract_address,
        )
        return log_receipts

    def decode_event(self, log_receipt: LogReceipt) -> Optional[EventData]:
        """
        :param log_receipt:
        :return: Decode `log_receipt` using all the possible ABIs for the topic. Returns `EventData` if successful,
            or `None` if decoding was not possible
        """
        for event_to_listen in self.events_to_listen[log_receipt["topics"][0].hex()]:
            # Try to decode using all the existing ABIs
            # One topic can have multiple matching ABIs due to `indexed` elements changing how to decode it
            try:
                return event_to_listen.process_log(log_receipt)
            except (LogTopicError, DecodingError):
                continue

        logger.error(
            "%s: Unexpected log format for log-receipt %s",
            self.__class__.__name__,
            log_receipt,
        )
        return None

    def decode_events(self, log_receipts: Sequence[LogReceipt]) -> List[EventData]:
        """
        :param log_receipts:
        :return: Decode `log_receipts` and return a list of `EventData`. If a `log_receipt` cannot be decoded
            `EventData` it will be skipped
        """
        decoded_elements = []
        for log_receipt in log_receipts:
            if decoded_element := self.decode_event(log_receipt):
                decoded_elements.append(decoded_element)
        return decoded_elements

    def get_unprocessed_events(
        self, log_receipts: Sequence[LogReceipt]
    ) -> Sequence[LogReceipt]:
        """
        Get the log_receipts events that were not stored as processed in the memory cache

        :param log_receipts:
        :return: unprocessed log_receipts
        """
        return [
            log_receipt
            for log_receipt in log_receipts
            if not self.element_already_processed_checker.is_processed(
                log_receipt["transactionHash"],
                log_receipt["blockHash"],
                log_receipt["logIndex"],
            )
        ]

    def set_processed_events(self, log_receipts: Sequence[LogReceipt]):
        """
        Set the log_receipts events as processed in the memory cache

        :param log_receipts:
        :return:
        """
        for log_receipt in log_receipts:
            self.element_already_processed_checker.mark_as_processed(
                log_receipt["transactionHash"],
                log_receipt["blockHash"],
                log_receipt["logIndex"],
            )

    @abstractmethod
    def process_decoded_events(self, decoded_events: List[EventData]):
        """
        Function to implement custom logic to process the decoded_events

        :param decoded_events:
        :return:
        """
        pass

    def index_until_last_chain_block(
        self,
        from_block_number: Optional[int] = None,
        update_last_indexed_block: Optional[bool] = True,
    ):
        """
        Run the indexer from the last indexed block until current last generated block on chain.
        Updates the last indexed block in database.
        """
        last_current_block = self.get_current_last_block()
        from_block = (
            from_block_number
            if from_block_number
            else self.get_from_block_number(self.contract_address)
        )
        logger.info(
            "%s: Starting indexing for pending-blocks=%d",
            self.__class__.__name__,
            last_current_block - from_block,
        )

        while from_block < last_current_block - self.blocks_behind:
            to_block = self.get_to_block_number(from_block, last_current_block)
            logger.info(
                "%s: Indexing from-block-number=%d to-block-number=%d pending-blocks=%d",
                self.__class__.__name__,
                from_block,
                to_block,
                last_current_block - to_block,
            )
            try:
                log_receipts = self.find_relevant_log_events(from_block, to_block)
            except FindRelevantEventsException:
                self.reset_block_process_limit()
                break

            if log_receipts:
                unprocessed_events = self.get_unprocessed_events(log_receipts)
                logger.info(
                    "%s: Processing %d events from %d events",
                    self.__class__.__name__,
                    len(unprocessed_events),
                    len(log_receipts),
                )
                decoded_events: List[EventData] = self.decode_events(unprocessed_events)
                # Store events in database
                self.process_decoded_events(decoded_events)
                # Mark events as processed
                self.set_processed_events(unprocessed_events)
            # Update from block
            from_block = to_block
            if update_last_indexed_block:
                # Update last block indexed
                self.set_last_indexed_block(self.contract_address, from_block)

        logger.info(
            "%s: Finalizing indexing cycle with pending-blocks=%d",
            self.__class__.__name__,
            last_current_block - from_block,
        )
