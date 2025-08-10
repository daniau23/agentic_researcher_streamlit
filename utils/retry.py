import time
import functools

def retry(exceptions, tries=3, delay=2, backoff=2):
    """
    Retry decorator with exponential backoff.

    Args:
        exceptions (tuple): exceptions to catch and retry on.
        tries (int): number of attempts.
        delay (int): initial delay between retries.
        backoff (int): multiplier for delay.

    Usage:
        @retry((TimeoutError, SomeOtherError))
        def func(...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Warning: {e}, retrying in {_delay} seconds...")
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator
