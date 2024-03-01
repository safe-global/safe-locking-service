import time
from contextlib import contextmanager
from logging import getLogger

from django.conf import settings

from eth_typing import ChecksumAddress

from gnosis.eth.ethereum_client import EthereumClientProvider

from safe_locking_service.locking_events.models import StatusEventsIndexer

logger = getLogger(__name__)


class BlockEventsManager:
    def __init__(self, *args, **kwargs):
        self.block_process_limit = settings.ETH_EVENTS_BLOCK_PROCESS_LIMIT
        self.block_process_limit_max = settings.ETH_EVENTS_BLOCK_PROCESS_LIMIT_MAX
        self.ethereum_client = EthereumClientProvider()
        self.blocks_behind = settings.ETH_EVENTS_BLOCKS_BEHIND
        self.enable_auto_block_process_limit = settings.ENABLE_AUTO_BLOCK_PROCESS_LIMIT

    @contextmanager
    def auto_adjust_block_limit(self, from_block_number: int, to_block_number: int):
        """
        Optimize number of queried blocks every time (block process limit)
        based on how fast the block interval is retrieved
        """

        # Check that we are processing the `block_process_limit`, if not, measures are not valid
        if not (
            self.enable_auto_block_process_limit
            and (1 + to_block_number - from_block_number) == self.block_process_limit
        ):
            # Auto adjustment disabled
            yield
        else:
            start = int(time.time())
            yield
            delta = int(time.time()) - start
            if delta > 30:
                self.block_process_limit = max(self.block_process_limit // 2, 1)
                logger.info(
                    "%s: block_process_limit halved to %d",
                    self.__class__.__name__,
                    self.block_process_limit,
                )
            elif delta > 10:
                new_block_process_limit = max(self.block_process_limit - 20, 1)
                self.block_process_limit = new_block_process_limit
                logger.info(
                    "%s: block_process_limit decreased to %d",
                    self.__class__.__name__,
                    self.block_process_limit,
                )
            elif delta < 2:
                self.block_process_limit *= 2
                logger.info(
                    "%s: block_process_limit duplicated to %d",
                    self.__class__.__name__,
                    self.block_process_limit,
                )
            elif delta < 5:
                self.block_process_limit += 20
                logger.info(
                    "%s: block_process_limit increased to %d",
                    self.__class__.__name__,
                    self.block_process_limit,
                )

            if (
                self.block_process_limit_max
                and self.block_process_limit > self.block_process_limit_max
            ):
                logger.info(
                    "%s: block_process_limit %d is bigger than block_process_limit_max %d, reducing",
                    self.__class__.__name__,
                    self.block_process_limit,
                    self.block_process_limit_max,
                )
                self.block_process_limit = self.block_process_limit_max

    def get_current_last_block(self):
        return self.ethereum_client.current_block_number

    def get_to_block(self, from_block_number: int, last_block: int):
        return min(
            from_block_number + self.block_process_limit - 1,
            last_block - self.blocks_behind,
        )

    def get_from_block(self, address: ChecksumAddress):
        last_indexed_block = StatusEventsIndexer.objects.get(
            contract=address
        ).last_indexed_block
        return (
            last_indexed_block
            if last_indexed_block
            else StatusEventsIndexer.objects.get(contract=address).deployed_block
        )

    def set_last_indexed_block(self, address: ChecksumAddress, block_number: int):
        StatusEventsIndexer.objects.filter(contract=address).update(
            last_indexed_block=block_number
        )

    def reset_block_process_limit(self):
        self.block_process_limit = settings.ETH_EVENTS_BLOCK_PROCESS_LIMIT
