import json
import os
from typing import Optional

from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from gnosis.eth.ethereum_client import EthereumClient


def get_locking_contract_abi():
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "abis", "safe_locking.json")
    )
    with open(path) as f:
        return json.load(f)


def get_locking_contract(
    w3: Web3, address: Optional[ChecksumAddress] = None
) -> Contract:
    contract_abi = get_locking_contract_abi()
    return w3.eth.contract(
        address=address, abi=contract_abi["abi"], bytecode=contract_abi.get("bytecode")
    )


def deploy_locking_contract(
    ethereum_client: EthereumClient,
    deployer: LocalAccount,
    tokenAddress: ChecksumAddress,
    cooldownPeriod: Optional[int] = 1,
) -> Contract:
    contract = get_locking_contract(ethereum_client.w3)
    tx = contract.constructor(
        deployer.address, tokenAddress, cooldownPeriod
    ).build_transaction(
        {
            "nonce": ethereum_client.w3.eth.get_transaction_count(
                deployer.address, block_identifier="pending"
            )
        }
    )
    signed_tx = deployer.sign_transaction(tx)
    tx_hash = ethereum_client.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    tx_receipt = ethereum_client.w3.eth.wait_for_transaction_receipt(tx_hash)

    return get_locking_contract(ethereum_client.w3, tx_receipt["contractAddress"])
