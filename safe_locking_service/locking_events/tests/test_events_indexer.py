from django.test import TestCase

from gnosis.eth.tests.ethereum_test_case import EthereumTestCaseMixin

from ..contracts.locking_contract import deploy_locking_contract


class TestEventsIndexer(EthereumTestCaseMixin, TestCase):
    # Just testing, will be the setup when add indexer tests
    def test_deploy_locking_contract(self):
        account = self.ethereum_test_account
        amount = 10
        erc20_contract = self.deploy_example_erc20(amount, account.address)
        locking_contract = deploy_locking_contract(
            self.ethereum_client, account, erc20_contract.address
        )
        self.assertIsNotNone(locking_contract.address)
