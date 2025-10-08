import functools
import os
import weakref

import multiprocessing
from time import sleep
from datetime import datetime
from abc import ABC, abstractmethod
from glob import glob
from pydantic import BaseModel, Field
from tornado import ioloop
from tornado import process
from yitool.log import logger

import typing
from typing import Callable, Dict, Sequence, Optional


if typing.TYPE_CHECKING:
    from typing import List, Optional, Union  # noqa: F401
    

class ModifiedModel(BaseModel):
    key: str = Field(default=None, description="更新的key")
    old_time: datetime = Field(default=None, description="之前的时间")
    new_time: datetime = Field(default=None, description="最近更新的时间")
    
class Modified(ABC):
    _queue: multiprocessing.Queue
    _updating: bool = False # 是否正在更新时间字典的标记
    _update_times: Dict[str, datetime] = dict({}) # 更新时间记录器
    _sorted_update_keys: Optional[dict[str, int]] = None # 更新时间记录器的key排序
    _io_loops = weakref.WeakKeyDictionary()
    _scheduler = None

    def __init__(
            self, 
            queue: multiprocessing.Queue,
            update_times: Dict[str, datetime] = {},
            sorted_update_keys: Optional[Sequence[str]] = None,
        ) -> None:
        self._queue = queue
        self._io_loops = weakref.WeakKeyDictionary()
        self._update_times = update_times
        self._sorted_update_keys = {k: i for i, k in enumerate(sorted_update_keys)} if sorted_update_keys is not None else None
        self._updating = False
    @property
    def update_times(self) -> Dict[str, datetime]:
        return self._update_times
    def start(self, check_time: int = 300) -> None:
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
            self._loop, self._update_times)
        self._scheduler = ioloop.PeriodicCallback(callback, check_time)
        self._scheduler.start()
        
    def stop(self) -> None:
        """Stops watching source data for changes.
        """
        if self._scheduler is not None:
            self._scheduler.stop()
            self._scheduler = None
        self._io_loops.clear()

    def _loop(self, update_times: Dict[str, datetime]) -> None:
        if self._updating:
            # 已经在重新加载，不需要再重试了.
            return
        if process.task_id() is not None:
            # We're in a child process created by fork_processes.  If child
            # processes restarted themselves, they'd all restart and then
            # all call fork_processes again.
            return
        self._updating = True
        new_update_times = self.fetch_update_times()
        items = new_update_times.items()
        if self._sorted_update_keys is not None:
            default_index = len(self._sorted_update_keys)
            items = sorted(items, key=lambda x: self._sorted_update_keys.get(x[0], default_index))
        for update_key, new_update_time in items:
            if update_key not in self._update_times:
                self._update_times[update_key] = new_update_time
                continue
            old_update_time = self._update_times.get(update_key)
            if new_update_time > old_update_time:
                logger.debug(f'notify, [{update_key}] {old_update_time} -> {new_update_time}')
                ret = self.notify(ModifiedModel(key=update_key, old_time=old_update_time, new_time=new_update_time))
                if ret:
                    self._update_times[update_key] = new_update_time
        self._updating = False

    def notify(self, update_info: ModifiedModel) -> bool:
        if self._queue.full():
            print('queue full', self._queue)
            return False
        try:
            self._queue.put(update_info)
            return True
        except:
            return False

    @abstractmethod
    def fetch_update_times(self) -> Dict[str, datetime]:
        raise NotImplementedError()
    