from django.test import TestCase
from django.urls import reverse

from eth_account import Account
from rest_framework import status

from safe_locking_service.locking_events.models import (
    LockEvent,
    UnlockEvent,
    WithdrawnEvent,
)

from .factories import LockEventFactory
from .utils import add_sorted_events


class TestViews(TestCase):
    def test_about_view(self):
        url = reverse("v1:locking_events:about")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_all_events_view(self):
        not_checksumed_address = "0x15fc97934bd2d140cd1ccbf7B164dec7ff64e667"
        response = self.client.get(
            reverse("v1:locking_events:all-events", args=(not_checksumed_address,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        address = Account.create().address
        response = self.client.get(
            reverse("v1:locking_events:all-events", args=(address,)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 0)

        add_sorted_events(address, 1000, 500, 500)
        response = self.client.get(
            reverse("v1:locking_events:all-events", args=(address,)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 3)
        # Response should be sorted by "-timestamp"
        withdrawn_response_result = results[0]
        withdrawn_expected = WithdrawnEvent.objects.last()
        self.assertCountEqual(
            withdrawn_response_result,
            {
                "eventType": "WITHDRAWN",
                "executionDate": withdrawn_expected.get_serialized_timestamp(),
                "transactionHash": withdrawn_expected.ethereum_tx_id,
                "holder": withdrawn_expected.holder,
                "amount": withdrawn_expected.amount,
                "logIndex": withdrawn_expected.log_index,
                "unlockIndex": withdrawn_expected.unlock_index,
            },
        )

        unlock_response_result = results[1]
        unlock_expected = UnlockEvent.objects.last()
        self.assertCountEqual(
            unlock_response_result,
            {
                "eventType": "WITHDRAWN",
                "executionDate": unlock_expected.get_serialized_timestamp(),
                "transactionHash": unlock_expected.ethereum_tx_id,
                "holder": unlock_expected.holder,
                "amount": unlock_expected.amount,
                "logIndex": unlock_expected.log_index,
                "unlockIndex": unlock_expected.unlock_index,
            },
        )

        lock_response_result = results[2]
        lock_expected = LockEvent.objects.last()
        self.assertCountEqual(
            lock_response_result,
            {
                "eventType": "WITHDRAWN",
                "executionDate": lock_expected.get_serialized_timestamp(),
                "transactionHash": lock_expected.ethereum_tx_id,
                "holder": lock_expected.holder,
                "amount": lock_expected.amount,
                "logIndex": lock_expected.log_index,
            },
        )

    def test_get_leader_board_view(self):
        response = self.client.get(
            reverse("v1:locking_events:leaderboard"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 0)

        address = Account.create().address
        add_sorted_events(address, 1000, 500, 500)
        response = self.client.get(
            reverse("v1:locking_events:leaderboard"), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertCountEqual(
            response.json()["results"][0],
            {
                "position": 1,
                "holder": address,
                "lockedAmount": str(500),
                "unlockedAmount": str(500),
                "withdrawnAmount": str(500),
            },
        )

        address_2 = Account.create().address
        add_sorted_events(address_2, 1500, 500, 500)
        response = self.client.get(
            reverse("v1:locking_events:leaderboard"), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.maxDiff = None
        self.assertCountEqual(
            response.json()["results"],
            [
                {
                    "holder": address_2,
                    "position": 1,
                    "lockedAmount": str(1000),
                    "unlockedAmount": str(500),
                    "withdrawnAmount": str(500),
                },
                {
                    "holder": address,
                    "position": 2,
                    "lockedAmount": str(500),
                    "unlockedAmount": str(500),
                    "withdrawnAmount": str(500),
                },
            ],
        )

    def test_leader_board_position_view(self):
        not_checksumed_address = "0x15fc97934bd2d140cd1ccbf7B164dec7ff64e667"
        response = self.client.get(
            reverse("v1:locking_events:leaderboard", args=(not_checksumed_address,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        address = Account.create().address
        response = self.client.get(
            reverse("v1:locking_events:leaderboard", args=(address,)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        add_sorted_events(address, 1000, 500, 500)
        response = self.client.get(
            reverse("v1:locking_events:leaderboard", args=(address,)), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "holder": address,
                "position": 1,
                "lockedAmount": str(500),
                "unlockedAmount": str(500),
                "withdrawnAmount": str(500),
            },
        )

        address_2 = Account.create().address
        add_sorted_events(address_2, 1500, 500, 500)
        response = self.client.get(
            reverse("v1:locking_events:leaderboard", args=(address,)), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "holder": address,
                "position": 2,
                "lockedAmount": str(500),
                "unlockedAmount": str(500),
                "withdrawnAmount": str(500),
            },
        )

    def test_lock_events_view(self):
        not_checksumed_address = "0x15fc97934bd2d140cd1ccbf7B164dec7ff64e667"
        response = self.client.get(
            reverse("v1:locking_events:lock-events", args=(not_checksumed_address,)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

        address = Account.create().address
        response = self.client.get(
            reverse("v1:locking_events:lock-events", args=(address,)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
        self.assertEqual(response.data["count"], 0)
        LockEventFactory(holder=address, amount=100)
        response = self.client.get(
            reverse("v1:locking_events:lock-events", args=(address,)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        lock_response_result = results[0]
        lock_expected = LockEvent.objects.last()
        self.assertCountEqual(
            lock_response_result,
            {
                "executionDate": lock_expected.get_serialized_timestamp(),
                "transactionHash": lock_expected.ethereum_tx_id,
                "holder": lock_expected.holder,
                "amount": lock_expected.amount,
                "logIndex": lock_expected.log_index,
            },
        )
        new_lock_event = LockEventFactory(holder=address, amount=100)
        response = self.client.get(
            reverse("v1:locking_events:lock-events", args=(address,)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 2)
        # Should be returned ordered by -timestamp
        self.assertEqual(results[0]["transactionHash"], new_lock_event.ethereum_tx_id)
        self.assertEqual(results[1]["transactionHash"], lock_expected.ethereum_tx_id)
