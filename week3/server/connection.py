import logging
from contextlib import contextmanager

from actual import Actual
from actual.exceptions import ActualError

from server.config import get_config

logger = logging.getLogger(__name__)


@contextmanager
def get_actual():
    """Open a fresh Actual Budget connection. Yields an Actual instance."""
    config = get_config()
    kwargs = {
        "base_url": config.actual_server_url,
        "password": config.actual_password,
        "file": config.actual_file,
    }
    if config.actual_encryption_password:
        kwargs["encryption_password"] = config.actual_encryption_password

    try:
        with Actual(**kwargs) as actual:
            actual.download_budget()
            yield actual
    except ActualError as e:
        logger.error("Actual Budget connection error: %s", e)
        raise
    except ConnectionError as e:
        logger.error("Network error connecting to Actual Budget: %s", e)
        raise
