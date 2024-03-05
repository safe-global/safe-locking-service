# Expected to add indexing tasks
import contextlib

from celery import app
from celery.utils.log import get_task_logger
from redis.exceptions import LockError

from safe_locking_service.locking_events.indexers.safe_locking_events_indexer import (
    get_safe_locking_event_indexer,
)
from safe_locking_service.locking_events.utils import (
    LOCK_TIMEOUT,
    SOFT_TIMEOUT,
    only_one_running_task,
)

logger = get_task_logger(__name__)


@app.shared_task(
    bind=True,
    soft_time_limit=SOFT_TIMEOUT,
    time_limit=LOCK_TIMEOUT,
)
def index_locking_events_task(self):
    with contextlib.suppress(LockError):
        with only_one_running_task(self):
            logger.info("Start indexing locking events")
            locking_events_indexer = get_safe_locking_event_indexer()
            locking_events_indexer.index_until_last_chain_block()
