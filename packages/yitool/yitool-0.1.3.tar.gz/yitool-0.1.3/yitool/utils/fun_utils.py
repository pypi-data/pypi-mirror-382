import asyncio
import functools
import inspect
import types
from typing import Any, Callable


class FunUtils(object):
    """函数工具类"""
    
    @staticmethod
    def name(func: Callable) -> str:
        """Get the name of the given function."""
        if isinstance(func, functools.partial):
            return FunUtils.name(func.func)
        if hasattr(func, "__name__"):
            return func.__name__
        if hasattr(func, "__class__") and hasattr(func.__class__, "__name__"):
            return func.__class__.__name__
        return str(func)
    
    @staticmethod
    async def is_async(func: Callable) -> bool:
        """Check if the given function is an async function, including
        coroutine functions, async generators, and coroutine objects.
        """
        return (
            inspect.iscoroutinefunction(func)
            or inspect.isasyncgenfunction(func)
            or isinstance(func, types.CoroutineType)
            or isinstance(func, types.GeneratorType)
            and asyncio.iscoroutine(func)
            or isinstance(func, functools.partial)
            and await FunUtils.is_async(func.func)
        )
            
    @staticmethod
    async def async_execute(
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if await FunUtils.is_async(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)
    
    @staticmethod
    def execute(
        func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if asyncio.iscoroutinefunction(func):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                coro = func(*args, **kwargs)
                future = asyncio.run_coroutine_threadsafe(coro, loop)
                return future.result()
            else:
                return loop.run_until_complete(func(*args, **kwargs))
        return func(*args, **kwargs)

