import contextlib
from typing import Optional, Set

from django.core.signals import request_finished
from django.db import connection

from celery.app.task import Task as CeleryTask
from redis.exceptions import LockError

from safe_locking_service.locking_events.redis import get_redis

LOCK_TIMEOUT = 60 * 15  # 15 minutes
SOFT_TIMEOUT = 60 * 10  # 10 minutes
ACTIVE_LOCKS: Set[str] = set()  # Active redis locks, release them when worker stops
WORKER_STOPPED = set()  # Worker status


def close_gevent_db_connection() -> None:
    """
    Clean gevent db connections. Check `atomic block` to prevent breaking the tests (Django `TestCase` wraps tests
    inside an atomic block that rollbacks at the end of the test)
    https://github.com/jneight/django-db-geventpool#using-orm-when-not-serving-requests
    """
    if not connection.in_atomic_block:
        request_finished.send(sender="greenlet")


@contextlib.contextmanager
def only_one_running_task(
    task: CeleryTask,
    lock_name_suffix: Optional[str] = None,
    lock_timeout: Optional[int] = LOCK_TIMEOUT,
    gevent_enabled: bool = True,
):
    """
    Ensures one running task at the same, using `task` name as a unique key

    :param task: CeleryTask
    :param lock_name_suffix: A suffix for the lock name, in the case that the same task can be run at the same time
    when it has different arguments
    :param lock_timeout: How long the lock will be stored, in case worker is halted so key is not stored forever
    in Redis
    :param gevent_enabled: If `True`, `close_gevent_db_connection` will be called at the end
    :return: Instance of redis `Lock`
    :raises: LockError if lock cannot be acquired
    """
    if WORKER_STOPPED:
        raise LockError("Worker is stopping")
    redis = get_redis()
    lock_name = f"locks:tasks:{task.name}"
    if lock_name_suffix:
        lock_name += f":{lock_name_suffix}"
    with redis.lock(lock_name, blocking=False, timeout=lock_timeout) as lock:
        try:
            ACTIVE_LOCKS.add(lock_name)
            yield lock
            ACTIVE_LOCKS.remove(lock_name)
        finally:
            if gevent_enabled:
                # Needed for django-db-geventpool
                close_gevent_db_connection()
