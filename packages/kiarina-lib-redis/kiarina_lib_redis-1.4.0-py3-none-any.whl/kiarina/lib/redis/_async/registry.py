from typing import Any

import redis.asyncio as redis

from .._core.registry import get_redis as _get_redis


def get_redis(
    config_key: str | None = None,
    *,
    cache_key: str | None = None,
    use_retry: bool | None = None,
    url: str | None = None,
    **kwargs: Any,
) -> redis.Redis:
    """
    Get a Redis client.

    Args:
        config_key (str | None): The configuration key for the Redis client.
        cache_key (str | None): The cache key for the Redis client.
        use_retry (bool | None): Whether to use retry for the Redis client.
        url (str | None): The Redis URL.
        **kwargs: Additional keyword arguments for the Redis client.

    Returns:
        redis.Redis: The Redis client.
    """
    return _get_redis(
        "async",
        config_key,
        cache_key=cache_key,
        use_retry=use_retry,
        url=url,
        **kwargs,
    )
