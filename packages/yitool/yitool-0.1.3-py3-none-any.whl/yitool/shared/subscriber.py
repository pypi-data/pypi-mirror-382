import functools
import weakref

from multiprocessing import Queue
from time import sleep
from abc import ABC, abstractmethod
from tornado import ioloop
from tornado import process

import typing
from typing import Any, Callable

if typing.TYPE_CHECKING:
    from typing import List, Optional, Union  # noqa: F401

class Subscriber(ABC):
    _queue: Queue
    _busy: bool = False # 是否正在忙碌
    _io_loops = weakref.WeakKeyDictionary()
    _scheduler = None

    def __init__(self, queue: Queue) -> None:
        self._queue = queue
        self._busy = False
        self._io_loops = weakref.WeakKeyDictionary()

    def start(self, check_time: int = 30) -> None:
        """Begins watching source data for changes.
        """
        io_loop = ioloop.IOLoop.current()
        if io_loop in self._io_loops:
            return
        self._io_loops[io_loop] = True
        if len(self._io_loops) > 1:
            sleep(10)
            # logger.warning("started more than once in the same loop")
        callback: Callable = functools.partial(
            self._loop, self._queue)
        self._scheduler = ioloop.PeriodicCallback(callback, check_time)
        self._scheduler.start()
        
    def stop(self) -> None:
        """Stops watching source data for changes.
        """
        if self._scheduler is not None:
            self._scheduler.stop()
            self._scheduler = None
        self._io_loops.clear()

    def _loop(self, queue: Queue) -> None:
        if self._busy:
            # 忙碌中
            sleep(0.5)
            return
        if process.task_id() is not None:
            # We're in a child process created by fork_processes.  If child
            # processes restarted themselves, they'd all restart and then
            # all call fork_processes again.
            return
        self._busy = True
        if queue.empty():
            sleep(0.5)
        else:
            data = queue.get()
            self.process(data)
        self._busy = False

    @abstractmethod
    def process(self, data: Any) -> None:
        raise NotImplementedError("process must be implemented by Subscriber subclasses")
    
