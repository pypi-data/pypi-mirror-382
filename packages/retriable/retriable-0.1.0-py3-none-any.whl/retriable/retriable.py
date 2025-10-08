import time
from typing import Any, Callable, Generator, TypeVar
from contextlib import contextmanager


T = TypeVar('T')
def retriable(
    func: Callable[..., T],
    *args,

    max_retries: int = 3,
    sleep_secs:  float = 1.0,
    validate_value: Callable[[T], bool] | None = None,
    on_try: Callable[[int, int], None] | None = None,

    raise_final_exception: bool = True,
    debug: bool = False,
    **kwargs
) -> T:
    current_retries = 0
    exception: Exception | None = None

    while current_retries < max_retries:
        if on_try:
            on_try(current_retries+1, max_retries)

        try:
            value = func(*args, **kwargs)

            if validate_value and validate_value(value):
                return value
        except Exception as e:
            if debug:
                print(f'Exception: {e}')

            exception = e

        current_retries += 1
        if current_retries == max_retries - 1:
            break

        time.sleep(sleep_secs)

    if raise_final_exception and exception is not None:
        raise exception

    return None # type: ignore

@contextmanager
def retriable_ctm(
    func: Callable[..., T],
    *args,

    max_retries: int = 3,
    sleep_secs:  float = 1.0,
    validate_value: Callable[[T], bool] | None = None,
    on_try: Callable[[int, int], None] | None = None,

    raise_final_exception: bool = True,
    debug: bool = False,
    **kwargs
) -> Generator[T, Any, Any]:
    yield retriable(
        func,
        *args,
        max_retries=max_retries,
        sleep_secs=sleep_secs,
        validate_value=validate_value,
        on_try=on_try,
        raise_final_exception=raise_final_exception,
        debug=debug,
        **kwargs
    )
