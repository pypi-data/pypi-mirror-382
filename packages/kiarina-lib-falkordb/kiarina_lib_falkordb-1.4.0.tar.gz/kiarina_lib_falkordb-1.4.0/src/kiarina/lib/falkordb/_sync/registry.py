from typing import Any

from falkordb import FalkorDB  # type: ignore

from .._core.registry import get_falkordb as _get_falkordb


def get_falkordb(
    config_key: str | None = None,
    *,
    cache_key: str | None = None,
    use_retry: bool | None = None,
    url: str | None = None,
    **kwargs: Any,
) -> FalkorDB:
    """
    Get a FalkorDB client.

    Args:
        config_key (str | None): The configuration key for the FalkorDB client.
        cache_key (str | None): The cache key for the FalkorDB client.
        use_retry (bool | None): Whether to use retry for the FalkorDB client.
        url (str | None): The FalkorDB URL.
        **kwargs: Additional keyword arguments for the FalkorDB client.

    Returns:
        FalkorDB: The FalkorDB client.
    """
    return _get_falkordb(
        "sync",
        config_key,
        cache_key=cache_key,
        use_retry=use_retry,
        url=url,
        **kwargs,
    )
