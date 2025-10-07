import time
import redis
from redis.sentinel import Sentinel
from urllib.parse import urlparse
from pypeline.constants import (
    REDIS_SENTINEL_MASTER_NAME,
    DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT,
    DEFAULT_REDIS_SOCKET_TIMEOUT,
    DEFAULT_REDIS_RETRY_ON_TIMEOUT,
    DEFAULT_REDIS_SOCKET_KEEPALIVE,
    DEFAULT_REDIS_HEALTH_CHECK_INTERVAL,
)


class LockingParallelBarrier:
    def __init__(self, redis_url, task_key="task_counter", lock_key="task_lock"):
        # Connect to Redis using the provided URL
        if REDIS_SENTINEL_MASTER_NAME is not None:
            parsed_redis_url = urlparse(redis_url)
            redis_sentinel = Sentinel(
                sentinels=[(parsed_redis_url.hostname, parsed_redis_url.port)],
            )
            self.redis = redis_sentinel.master_for(
                REDIS_SENTINEL_MASTER_NAME,
                db=int(parsed_redis_url.path[1]) if parsed_redis_url.path else 0,
                password=parsed_redis_url.password,
                socket_connect_timeout=DEFAULT_REDIS_SOCKET_CONNECT_TIMEOUT,
                socket_timeout=DEFAULT_REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=DEFAULT_REDIS_RETRY_ON_TIMEOUT,
                socket_keepalive=DEFAULT_REDIS_SOCKET_KEEPALIVE,
                health_check_interval=DEFAULT_REDIS_HEALTH_CHECK_INTERVAL,
                decode_responses=True,
            )
        else:
            self.redis = redis.StrictRedis.from_url(redis_url, decode_responses=True)
        self.task_key = task_key
        self.lock_key = lock_key

    def acquire_lock(self, timeout=5):
        """Acquire a lock using Redis."""
        while True:
            if self.redis.set(self.lock_key, "locked", nx=True, ex=timeout):
                return True
            time.sleep(0.1)

    def release_lock(self):
        """Release the lock in Redis."""
        self.redis.delete(self.lock_key)

    def set_task_count(self, count):
        """Initialize the task counter in Redis."""
        self.redis.set(self.task_key, count)

    def decrement_task_count(self):
        """Decrement the task counter in Redis."""
        return self.redis.decr(self.task_key)

    def task_exists(self):
        return self.redis.exists(self.task_key)

    def get_task_count(self):
        """Get the current value of the task counter."""
        return int(self.redis.get(self.task_key) or 0)
