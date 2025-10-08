import time
from collections.abc import Callable

from toucan.utils import logger


def retry_action(
    action: Callable, *args, retry_times: int = 3, delay: float = 1.0, post_fail_action: Callable = None, **kwargs
):
    """
    Retry an action a specified number of times with an optional delay between retries.
    :param action: The action to retry.
    :param args: Arguments of the action.
    :param retry_times: Number of times to retry the action.
    :param delay: Delay between retries.
    :param kwargs: Keyword arguments of the action.
    """
    if retry_times == 1:
        return action(*args, **kwargs)
    try:
        return action(*args, **kwargs)
    except Exception:
        if post_fail_action:
            post_fail_action()
        time.sleep(delay)
        logger.warn('Method call failed, retrying...')
        return retry_action(action, *args, retry_times=retry_times - 1, delay=delay, **kwargs)
