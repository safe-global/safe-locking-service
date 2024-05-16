import csv
from datetime import date
from io import StringIO

from eth_account import Account
from faker import Faker

fake = Faker(0)


class CSVFactory:
    # Headers as specified
    headers = [
        "safe_address",
        "period_start",
        "period_end",
        "total_points",
        "boost",
        "total_boosted_points",
        "points_rank",
        "boosted_points_rank",
    ]

    def create(self, num_records=100):
        output = StringIO()
        try:
            writer = csv.DictWriter(output, fieldnames=self.headers)
            writer.writeheader()  # Write the headers

            for _ in range(num_records):
                data = {
                    "safe_address": Account().create().address,
                    "period_start": date.today(),
                    "period_end": date.today(),
                    "total_points": fake.pyint(),
                    "boost": fake.pydecimal(left_digits=7, right_digits=8),
                    "total_boosted_points": fake.pydecimal(
                        left_digits=7, right_digits=8
                    ),
                    "points_rank": fake.pyint(),
                    "boosted_points_rank": fake.pyint(),
                }
                writer.writerow(data)
            return output.getvalue()
        finally:
            output.close()
