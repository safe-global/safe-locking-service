from io import StringIO
from unittest import mock
from unittest.mock import PropertyMock

from django.core.management import CommandError, call_command
from django.test import TestCase

from gnosis.eth.ethereum_client import EthereumClient

from ..indexers.events_indexer import logger as events_logger


class TestCommands(TestCase):
    @mock.patch.object(
        EthereumClient, "current_block_number", new_callable=PropertyMock
    )
    def test_reindex_locking_events(self, mock_current_block):
        command = "reindex_locking_events"

        with self.assertRaisesMessage(
            CommandError, "the following arguments are required: --from-block-number"
        ):
            call_command(command)
        mock_current_block.return_value = 100

        # Auto adjust block process_limit
        buf = StringIO()
        call_command(
            command,
            "--from-block-number=101",
            stdout=buf,
        )
        self.assertIn("Setting auto adjust block-process-limit", buf.getvalue())
        self.assertIn("Setting from-block-number to 101", buf.getvalue())
        # Configured block process_limit
        buf = StringIO()
        call_command(
            command,
            "--block-process-limit=10",
            "--from-block-number=101",
            stdout=buf,
        )
        self.assertIn("Setting block-process-limit to 10", buf.getvalue())
        self.assertIn("Setting from-block-number to 101", buf.getvalue())

        mock_current_block.return_value = 200
        buf = StringIO()
        with self.assertLogs(logger=events_logger) as cm:
            call_command(
                command,
                "--block-process-limit=51",
                "--from-block-number=100",
                stdout=buf,
            )
            self.assertIn("Setting block-process-limit to 51", buf.getvalue())
            self.assertIn("Setting from-block-number to 100", buf.getvalue())
            self.assertIn(
                "Starting indexing for pending-blocks=100",
                cm.output[0],
            )
            self.assertIn(
                "Indexing from-block-number=100 to-block-number=150 pending-blocks=50",
                cm.output[1],
            )
            self.assertIn(
                "Indexing from-block-number=150 to-block-number=200 pending-blocks=0",
                cm.output[2],
            )
            self.assertIn(
                "Finalizing indexing cycle with pending-blocks=0",
                cm.output[3],
            )
