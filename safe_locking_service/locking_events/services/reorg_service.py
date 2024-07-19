import logging
from functools import cache
from typing import Optional

from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction

from hexbytes import HexBytes

from gnosis.eth import EthereumClient
from gnosis.eth.ethereum_client import get_auto_ethereum_client

from safe_locking_service.locking_events.indexers.safe_locking_events_indexer import (
    get_safe_locking_event_indexer,
)
from safe_locking_service.locking_events.models import EthereumTx

logger = logging.getLogger(__name__)


@cache
def get_reorg_service():
    return ReorgService(ethereum_client=get_auto_ethereum_client())


class ReorgService:
    def __init__(
        self,
        ethereum_client: EthereumClient,
        eth_reorg_blocks: int = settings.INDEXER_REORG_BLOCKS,
        eth_reorg_blocks_batch: int = settings.INDEXER_BLOCK_REORG_BATCH,
    ):
        """
        :param ethereum_client:
        :param eth_reorg_blocks: Minimum number of blocks to consider a block confirmed and safe to rely on. In Mainnet
            10 blocks is considered safe
        """
        self.ethereum_client = ethereum_client
        self.eth_reorg_blocks = eth_reorg_blocks
        self.eth_reorg_blocks_batch = eth_reorg_blocks_batch

    def check_reorg(
        self, database_blocks, blockchain_blocks, confirmation_block
    ) -> Optional[int]:
        """

        :param database_blocks:
        :param blockchain_blocks:
        :param confirmation_block:
        :return block number of reorg block if reorg is detected:
        """
        blocks_to_confirm = []
        reorg_block: Optional[int] = None
        for database_block, blockchain_block in zip(database_blocks, blockchain_blocks):
            if HexBytes(blockchain_block["hash"]) == HexBytes(
                database_block.block_hash
            ):
                # Check all the blocks but only mark safe ones as confirmed
                if database_block.block_number <= confirmation_block:
                    logger.debug(
                        "Block with number=%d and hash=%s is matching blockchain one, setting as confirmed",
                        database_block.block_number,
                        HexBytes(blockchain_block["hash"]).hex(),
                    )
                    database_block.confirmed = True
                    blocks_to_confirm.append(database_block)
            else:
                logger.warning(
                    "Block with number=%d and hash=%s is not matching blockchain hash=%s, reorg found",
                    database_block.block_number,
                    HexBytes(database_block.block_hash).hex(),
                    HexBytes(blockchain_block["hash"]).hex(),
                )
                reorg_block = database_block.block_number
                break
        # Update confirmed blocks
        EthereumTx.objects.bulk_update(blocks_to_confirm, ["confirmed"])
        return reorg_block

    def run_check_reorg(self):
        """
        :return: Number of the oldest block with reorg detected. `None` if not reorg found
        """
        unconfirmed_blocks = (
            EthereumTx.objects.not_confirmed()
            .only("block_number", "block_hash")
            .order_by("block_number")
        )
        if not unconfirmed_blocks:
            return None
        current_block_number = self.ethereum_client.current_block_number
        confirmation_block = current_block_number - self.eth_reorg_blocks
        paginator = Paginator(unconfirmed_blocks, per_page=self.eth_reorg_blocks_batch)
        for page_number in paginator.page_range:
            current_page = paginator.get_page(page_number)
            database_blocks = []
            block_numbers = []
            for block in current_page.object_list:
                database_blocks.append(block)
                block_numbers.append(block.block_number)
            blockchain_blocks = self.ethereum_client.get_blocks(
                block_numbers, full_transactions=False
            )
            if reorg_block_number := self.check_reorg(
                database_blocks, blockchain_blocks, confirmation_block
            ):
                return reorg_block_number

    def reset_indexer(self, reorg_block_number: int):
        locking_indexer = get_safe_locking_event_indexer()
        # Clean cached elements.
        locking_indexer.element_already_processed_checker.clear()
        # Reset indexer until reorg block
        locking_indexer.set_last_indexed_block(
            locking_indexer.contract_address, reorg_block_number
        )

    @transaction.atomic
    def recover_from_reorg(self, reorg_block_number: int) -> int:
        """
        Reset database fields to a block to start reindexing from that block
        and remove blocks greater or equal than `reorg_block_number`.

        :param reorg_block_number:
        :return: Return number of elements updated
        """

        self.reset_indexer(reorg_block_number)
        # Delete transactions from reorg
        number_deleted_blocks, _ = EthereumTx.objects.filter(
            block_number__gte=reorg_block_number
        ).delete()
        logger.warning(
            "Reorg of block-number=%d fixed, indexing was reset to block=%d, %d blocks were deleted",
            reorg_block_number,
            reorg_block_number,
            number_deleted_blocks,
        )
        return number_deleted_blocks
