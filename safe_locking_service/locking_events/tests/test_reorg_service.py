from unittest import mock
from unittest.mock import MagicMock, PropertyMock

from django.test import TestCase

from gnosis.eth import EthereumClient

from ..models import EthereumTx
from ..services.reorg_service import get_reorg_service
from .factories import EthereumTxFactory
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
        self.assertEqual(reorg_service.check_reorgs(), block_number)

        ethereum_block.block_hash = block["hash"]
        ethereum_block.save(update_fields=["block_hash"])
        self.assertIsNone(reorg_service.check_reorgs())
        ethereum_block.refresh_from_db()
        self.assertTrue(ethereum_block.confirmed)
