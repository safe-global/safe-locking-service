from datetime import timedelta

from django.utils import timezone

from eth_account.signers.local import LocalAccount
from eth_typing import ChecksumAddress
from web3 import Web3
from web3.contract import Contract

from .factories import LockEventFactory, UnlockEventFactory, WithdrawnEventFactory


def erc20_approve(
    w3: Web3,
    signer_account: LocalAccount,
    erc20_contract: Contract,
    spender: ChecksumAddress,
    amount: int,
):
    tx_approval = erc20_contract.functions.approve(spender, amount).build_transaction(
        {
            "from": signer_account.address,
            "nonce": w3.eth.get_transaction_count(signer_account.address),
        }
    )
    signed_tx = signer_account.sign_transaction(tx_approval)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def locking_contract_lock(
    w3: Web3, signer_account: LocalAccount, locking_contract: Contract, amount: int
):
    tx_lock = locking_contract.functions.lock(amount).build_transaction(
        {
            "from": signer_account.address,
            "nonce": w3.eth.get_transaction_count(signer_account.address),
        }
    )
    signed_tx = signer_account.sign_transaction(tx_lock)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def locking_contract_unlock(
    w3: Web3, signer_account: LocalAccount, locking_contract: Contract, amount: int
):
    tx_lock = locking_contract.functions.unlock(amount).build_transaction(
        {
            "from": signer_account.address,
            "nonce": w3.eth.get_transaction_count(signer_account.address),
        }
    )
    signed_tx = signer_account.sign_transaction(tx_lock)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def add_sorted_events(
    address: ChecksumAddress,
    lock_amount: int,
    unlock_umount: int,
    withdrawn_amount: int,
):
    """
    Add one event for each type in order (lock, unlock, withdraw)

    :param address:
    :param lock_amount:
    :param unlock_umount:
    :param withdrawn_amount:
    :return:
    """
    LockEventFactory(
        holder=address,
        amount=lock_amount,
        timestamp=timezone.now() - timedelta(days=2),
    )
    UnlockEventFactory(
        holder=address,
        amount=unlock_umount,
        timestamp=timezone.now() - timedelta(days=1),
    )
    WithdrawnEventFactory(
        holder=address, amount=withdrawn_amount, timestamp=timezone.now()
    )
