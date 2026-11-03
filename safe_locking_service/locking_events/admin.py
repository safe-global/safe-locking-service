from abc import abstractmethod
from typing import Union

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from safe_eth.eth.django.admin import AdvancedAdminSearchMixin
from safe_eth.eth.ethereum_client import get_auto_ethereum_client
from safe_eth.eth.ethereum_network import EthereumNetwork

from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)

# safe-eth-py v7 removed the Etherscan client that provided the explorer url
ETHERSCAN_URLS = {
    EthereumNetwork.MAINNET: "https://etherscan.io",
    EthereumNetwork.SEPOLIA: "https://sepolia.etherscan.io",
}


class TxHashEtherscanMixin:
    @abstractmethod
    def get_tx_hash(self, obj):
        pass

    def tx_hash_etherscan_link(
        self, obj: Union[EthereumTx, LockEvent, UnlockEvent, WithdrawnEvent]
    ) -> SafeString:
        """
        Return the etherscan link for every transaction hash

        :param obj:
        :return:
        """
        ethereum_client = get_auto_ethereum_client()
        etherscan_url = ETHERSCAN_URLS.get(
            EthereumNetwork(ethereum_client.get_chain_id())
        )
        if not etherscan_url:
            return self.get_tx_hash(obj)

        return format_html(
            '<a href="{}/tx/{}">{}</a>',
            etherscan_url,
            self.get_tx_hash(obj),
            self.get_tx_hash(obj),
        )

    tx_hash_etherscan_link.short_description = "Tx hash etherscan link"
    tx_hash_etherscan_link.allow_tags = True


@admin.register(EthereumTx)
class EthereumTxAdmin(AdvancedAdminSearchMixin, admin.ModelAdmin, TxHashEtherscanMixin):
    list_display = (
        "block_timestamp",
        "tx_hash_etherscan_link",
        "block_number",
        "block_hash",
        "confirmed",
    )
    ordering = ["-block_timestamp"]
    list_filter = ("confirmed",)
    search_fields = ["==tx_hash"]

    def get_tx_hash(self, obj: EthereumTx):
        return obj.tx_hash


@admin.register(LockEvent, UnlockEvent, WithdrawnEvent)
class CommonEventAdmin(
    AdvancedAdminSearchMixin, admin.ModelAdmin, TxHashEtherscanMixin
):
    list_display = (
        "timestamp",
        "tx_hash_etherscan_link",
        "holder",
        "amount",
    )
    ordering = ["-timestamp"]
    search_fields = ["==ethereum_tx_id", "==holder"]

    def get_tx_hash(self, obj: Union[LockEvent, UnlockEvent, WithdrawnEvent]):
        return obj.ethereum_tx_id
