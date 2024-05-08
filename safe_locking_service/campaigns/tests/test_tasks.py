from django.test import TestCase

from eth_account import Account
from faker import Faker

from ..models import Activity
from ..tasks import process_csv_task
from .factories import PeriodFactory

fake = Faker()


def activity_entry():
    return {
        "safe_address": Account.create().address,
        "total_points": fake.pyint(),
        "boost": fake.pydecimal(left_digits=7, right_digits=8),
        "total_boosted_points": fake.pydecimal(left_digits=7, right_digits=8),
        "points_rank": fake.pyint(),
        "boosted_points_rank": fake.pyint(),
    }


class ProcessCSVTestCase(TestCase):
    def setUp(self):
        self.period = PeriodFactory()

    def test_process_csv_success(self):
        activity_1 = activity_entry()
        activity_2 = activity_entry()

        process_csv_task(
            self.period.id,
            [
                activity_1,
                activity_2,
            ],
        )

        self.assertEqual(Activity.objects.filter(period=self.period).count(), 2)
        actual_activity1 = Activity.objects.get(address=activity_1["safe_address"])
        actual_activity2 = Activity.objects.get(address=activity_2["safe_address"])
        self.assertEqual(activity_1["total_points"], actual_activity1.total_points)
        self.assertEqual(activity_1["boost"], actual_activity1.boost)
        self.assertEqual(
            activity_1["total_boosted_points"], actual_activity1.total_boosted_points
        )
        self.assertEqual(activity_2["total_points"], actual_activity2.total_points)
        self.assertEqual(activity_2["boost"], actual_activity2.boost)
        self.assertEqual(
            activity_2["total_boosted_points"], actual_activity2.total_boosted_points
        )

    def test_process_csv_clear_activities(self):
        activity = activity_entry()
        new_activity = activity_entry()

        process_csv_task(self.period.id, [activity])
        process_csv_task(self.period.id, [new_activity])

        self.assertEqual(Activity.objects.filter(period=self.period).count(), 1)
        actual_new_activity = Activity.objects.get(address=new_activity["safe_address"])
        self.assertEqual(new_activity["total_points"], actual_new_activity.total_points)
        self.assertEqual(new_activity["boost"], actual_new_activity.boost)
        self.assertEqual(
            new_activity["total_boosted_points"],
            actual_new_activity.total_boosted_points,
        )
