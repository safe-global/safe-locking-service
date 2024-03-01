from django.test import TestCase

from gnosis.eth.tests.ethereum_test_case import EthereumTestCaseMixin

from ..contracts.locking_contract import deploy_locking_contract
from ..indexers.safe_locking_events_indexer import (
    SafeLockingEventsIndexer,
    get_safe_locking_event_indexer,
)
from ..models import EthereumTx, StatusEventsIndexer


class TestLockingEventsIndexer(EthereumTestCaseMixin, TestCase):
    def setUp(self) -> None:
        account = self.ethereum_test_account
        amount = 10000000
        self.erc20_contract = self.deploy_example_erc20(amount, account.address)
        self.locking_contract = deploy_locking_contract(
            self.ethereum_client, account, self.erc20_contract.address
        )
        self.locking_contract_address = self.locking_contract.address
        self.assertIsNotNone(self.locking_contract.address)
        StatusEventsIndexer.objects.create(
            contract=self.locking_contract_address,
            deployed_block=0,
            last_indexed_block=0,
        )

    def test_get_safe_locking_event_indexer(self):
        with self.settings(SAFE_LOCKING_CONTRACT_ADDRESS=self.locking_contract_address):
            locking_events_indexer = get_safe_locking_event_indexer()
            self.assertEqual(
                locking_events_indexer.contract_address, self.locking_contract_address
            )
            self.assertEqual(locking_events_indexer, get_safe_locking_event_indexer())

    def test_index_lock_events(self):
        account = self.ethereum_test_account
        # TODO Refactor erc20 approve
        tx_approval = self.erc20_contract.functions.approve(
            self.locking_contract.address, 10
        ).build_transaction(
            {
                "from": account.address,
                "nonce": self.ethereum_client.w3.eth.get_transaction_count(
                    account.address
                ),
            }
        )
        signed_tx = account.sign_transaction(tx_approval)
        tx_hash = self.ethereum_client.w3.eth.send_raw_transaction(
            signed_tx.rawTransaction
        )
        tx_receipt = self.ethereum_client.w3.eth.wait_for_transaction_receipt(tx_hash)
        # TODO Refactor Safe lock
        tx_lock = self.locking_contract.functions.lock(10).build_transaction(
            {
                "from": account.address,
                "nonce": self.ethereum_client.w3.eth.get_transaction_count(
                    account.address
                ),
            }
        )
        signed_tx = account.sign_transaction(tx_lock)
        tx_hash = self.ethereum_client.w3.eth.send_raw_transaction(
            signed_tx.rawTransaction
        )
        tx_receipt = self.ethereum_client.w3.eth.wait_for_transaction_receipt(tx_hash)
        locking_events_indexer = SafeLockingEventsIndexer(self.locking_contract_address)
        locking_events_indexer.index_until_last_chain_block()
        self.assertEqual(EthereumTx.objects.count(), 1)
