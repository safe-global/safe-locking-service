# Expected to add indexing tasks
import contextlib

from celery import app
from celery.utils.log import get_task_logger
from redis.exceptions import LockError

from safe_locking_service.locking_events.indexers.safe_locking_events_indexer import (
    get_safe_locking_event_indexer,
)
from safe_locking_service.locking_events.services.reorg_service import (
    ReorgService,
    get_reorg_service,
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


@app.shared_task(
    bind=True,
    soft_time_limit=SOFT_TIMEOUT,
    time_limit=LOCK_TIMEOUT,
)
def check_reorgs_task(self):
    with contextlib.suppress(LockError):
        with only_one_running_task(self):
            logger.info("Start checking of reorgs")
            reorg_service: ReorgService = get_reorg_service()
            reorg_block_number = reorg_service.run_check_reorg()
            if reorg_block_number:
                logger.warning("Reorg found for block-number=%d", reorg_block_number)
                # Stopping running tasks is not possible with gevent
                reorg_service.recover_from_reorg(reorg_block_number)
                return reorg_block_number
