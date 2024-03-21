from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from django.test import TestCase

from gnosis.eth import EthereumClient

from ..indexers.safe_locking_events_indexer import get_safe_locking_event_indexer
from ..models import EthereumTx, LockEvent
from ..services.reorg_service import get_reorg_service
from .factories import EthereumTxFactory, LockEventFactory
from .mocks.mock_blocks import block_child, block_parent


class TestReorgService(TestCase):
    @mock.patch.object(EthereumClient, "get_blocks")
    @mock.patch.object(
        EthereumClient, "current_block_number", new_callable=PropertyMock
    )
    def test_check_reorgs(
        self, current_block_number_mock: PropertyMock, get_blocks_mock: MagicMock
    ):
        reorg_service = get_reorg_service()

        block = block_child
        block_number = block["number"]

        get_blocks_mock.return_value = [block_child, block_parent]
        current_block_number = block_number + 100
        current_block_number_mock.return_value = current_block_number

        ethereum_block: EthereumTx = EthereumTxFactory(
            block_number=block_number, confirmed=False
        )
        self.assertEqual(reorg_service.run_check_reorg(), block_number)

        ethereum_block.block_hash = block["hash"]
        ethereum_block.save(update_fields=["block_hash"])
        self.assertIsNone(reorg_service.run_check_reorg())
        ethereum_block.refresh_from_db()
        self.assertTrue(ethereum_block.confirmed)

    def test_recover_from_reorg(self):
        reorg_service = get_reorg_service()
        events_indexer = get_safe_locking_event_indexer()
        reorg_block = 2000  # Test a reorg in block 2000
        ethereum_txs = [
            EthereumTxFactory(block_number=reorg_block + i)
            for i in range(-1000, 1001, 500)
        ]
        self.assertEqual(
            events_indexer.get_from_block_number(events_indexer.contract_address), 0
        )
        events_indexer.set_last_indexed_block(events_indexer.contract_address, 3000)
        self.assertEqual(
            events_indexer.get_from_block_number(events_indexer.contract_address), 3000
        )
        for ethereum_tx in ethereum_txs:
            LockEventFactory(ethereum_tx=ethereum_tx)
        self.assertEqual(LockEvent.objects.count(), len(ethereum_txs))
        LockEventFactory(ethereum_tx=EthereumTxFactory(block_number=reorg_block))

        lock_events_from_reorg = LockEvent.objects.filter(
            ethereum_tx__block_number__gte=reorg_block
        ).count()
        self.assertEqual(lock_events_from_reorg, 4)

        transactions_from_reorg = EthereumTx.objects.filter(
            block_number__gte=reorg_block
        ).count()
        self.assertEqual(transactions_from_reorg, 4)

        reorg_service.recover_from_reorg(reorg_block)

        # Should remove transactions, events from reorg block and update the indexer status
        lock_events_from_reorg = LockEvent.objects.filter(
            ethereum_tx__block_number__gte=reorg_block
        ).count()
        self.assertEqual(lock_events_from_reorg, 0)
        transactions_from_reorg = EthereumTx.objects.filter(
            block_number__gte=reorg_block
        ).count()
        self.assertEqual(transactions_from_reorg, 0)
        self.assertEqual(
            events_indexer.get_from_block_number(events_indexer.contract_address), 2000
        )
