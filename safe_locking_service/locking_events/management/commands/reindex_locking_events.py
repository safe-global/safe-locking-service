from django.conf import settings
from django.core.management.base import BaseCommand

from ...indexers.safe_locking_events_indexer import SafeLockingEventsIndexer


class Command(BaseCommand):
    help = "Force reindexing of Safe locking contract events"

    def add_arguments(self, parser):
        parser.add_argument(
            "--block-process-limit",
            type=int,
            help="Number of blocks to query each time",
            default=None,
        )
        parser.add_argument(
            "--from-block-number",
            type=int,
            help="Which block to start reindexing from",
            required=True,
        )

    def handle(self, *args, **options):
        block_process_limit = options["block_process_limit"]
        from_block_number = options["from_block_number"]

        if block_process_limit:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Setting block-process-limit to {block_process_limit}"
                )
            )
            events_indexer = SafeLockingEventsIndexer(
                contract_address=settings.SAFE_LOCKING_CONTRACT_ADDRESS,
                block_process_limit=block_process_limit,
                enable_auto_block_process_limit=False,
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Setting auto adjust block-process-limit")
            )
            events_indexer = SafeLockingEventsIndexer(
                contract_address=settings.SAFE_LOCKING_CONTRACT_ADDRESS
            )

        self.stdout.write(
            self.style.SUCCESS(f"Setting from-block-number to {from_block_number}")
        )
        # Start indexer from block number
        events_indexer.index_until_last_chain_block(
            from_block_number=from_block_number, update_last_indexed_block=False
        )
