from typing import Union

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from gnosis.eth.clients.etherscan_client import EtherscanClient
from gnosis.eth.django.admin import AdvancedAdminSearchMixin
from gnosis.eth.ethereum_client import EthereumClientProvider
from gnosis.eth.ethereum_network import EthereumNetwork

from safe_locking_service.locking_events.models import (
    EthereumTx,
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)


@admin.register(EthereumTx)
class EthereumTxAdmin(AdvancedAdminSearchMixin, admin.ModelAdmin):
    list_display = (
        "block_timestamp",
        "tx_hash",
        "block_number",
        "block_hash",
        "confirmed",
    )
    ordering = ["-block_timestamp"]
    list_filter = ("confirmed",)
    search_fields = ["==tx_hash"]


@admin.register(LockEvent, UnlockEvent, WithdrawnEvent)
class CommonEventAdmin(AdvancedAdminSearchMixin, admin.ModelAdmin):
    list_display = (
        "timestamp",
        "ethereum_tx_id",
        "tx_etherscan_link",
        "holder",
        "amount",
    )
    ordering = ["-timestamp"]
    search_fields = ["==ethereum_tx_id", "==holder"]

    def tx_etherscan_link(
        self, obj: Union[LockEvent, UnlockEvent, WithdrawnEvent]
    ) -> SafeString:
        """
        Return the ether scan link by transaction hash

        :param obj:
        :return:
        """
        ethereum_client = EthereumClientProvider()
        etherscan = EtherscanClient(EthereumNetwork(ethereum_client.get_chain_id()))
        return format_html(
            '<a href="{}/tx/{}">{}</a>',
            etherscan.base_url,
            obj.ethereum_tx_id,
            obj.ethereum_tx_id,
        )

    tx_etherscan_link.short_description = "Etherscan link"
    tx_etherscan_link.allow_tags = True
