from typing import Any

from django.db import transaction

from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Activity, Period

BATCH_SIZE = 1000

logger = get_task_logger(__name__)


@shared_task()
def process_csv_task(period_id: int, activities_list: list[dict[str, Any]]) -> None:
    """
    Process a list of activities and store them in the database for a given Period.

    This function is designed to be executed as an asynchronous task. It processes a list
    of activities, deletes any existing activities for the given period, and then bulk
    inserts the new activities in batches to the database.


    @param period_id: The ID of the period for which the activities are to be processed.
    @param activities_list: A list of dictionaries, where each dictionary represents an activity.
    """
    logger.info("CSV processing started for period ID: %s", period_id)
    try:
        with transaction.atomic():
            period = Period.objects.get(id=period_id)

            logger.info("Deleting all activities for period: %s", period.slug)
            period.activities.all().delete()

            activities = []
            for input_activity in activities_list:
                activity = Activity(
                    period=period,
                    address=input_activity["safe_address"],
                    total_points=input_activity["total_points"],
                    boost=input_activity["boost"],
                    total_boosted_points=input_activity["total_boosted_points"],
                )
                # TODO if activity is not in the range of a Period, skip it
                activities.append(activity)

            for start in range(0, len(activities), BATCH_SIZE):
                Activity.objects.bulk_create(activities[start : start + BATCH_SIZE])

            logger.info("All activities created for period: %s", period.slug)
    except Exception as e:
        logger.error("Failed to process CSV for period ID %s: %s", period_id, str(e))
