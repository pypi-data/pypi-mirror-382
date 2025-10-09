from functools import wraps
from asyncio import get_event_loop, new_event_loop, set_event_loop, wrap_future, run_coroutine_threadsafe
from inspect import iscoroutinefunction
from threading import current_thread, main_thread
from typing import Callable


def add_sync_support_to_function(coroutine_function) -> Callable:
    main_loop = get_event_loop()

    @wraps(coroutine_function)
    def dual_purpose_function(*args, **kwargs):
        coroutine = coroutine_function(*args, **kwargs)
        try:
            loop = get_event_loop()
        except RuntimeError:
            loop = new_event_loop()
            set_event_loop(loop)
        if current_thread() is main_thread() or not main_loop.is_running():
            if loop.is_running():
                return coroutine
            return loop.run_until_complete(coroutine)
        if loop.is_running():
            async def coroutine_wrapper():
                return await wrap_future(run_coroutine_threadsafe(coroutine, main_loop))
            return coroutine_wrapper()
        return run_coroutine_threadsafe(coroutine, main_loop).result()

    return dual_purpose_function


def add_sync_support_to_object(obj):
    for name in dir(obj):
        attribute = getattr(obj, name)

        if name.startswith("_"):
            continue
        if not iscoroutinefunction(attribute):
            continue

        dual_purpose_method = add_sync_support_to_function(attribute)
        setattr(obj, name, dual_purpose_method)

    return obj
