import functools
from time import sleep
import weakref
from tornado import ioloop
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from yitool.enums import DATE_FORMAT
from yitool.log import logger
from yitool.shared.modified import ModifiedModel
from yitool.utils.date_utils import DateUtils
from yitool.yi_redis import YiRedis


class JobStore(object):
    """ 任务存储与调度 """

    def __init__(self, redis: YiRedis, redis_key: str, watching_keys: List[str],
                 storage_update_times: Dict[str, Optional[datetime]] = {}):
        self._redis = redis
        self._redis_key = redis_key
        # 初始化实例私有变量，防止类级别污染
        self._update_times: Dict[str, List[Optional[datetime]]] = {
            key: [value, None] for key, value in storage_update_times.items()
        }
        self._busy_dict: Dict[str, bool] = {val: False for val in watching_keys}
        self._job_dict: Dict[str, Any] = {}
        self._io_loops = weakref.WeakKeyDictionary()
        self._scheduler = None
        self._sync = None

    @property
    def jobs(self) -> List[str]:
        return list(self._update_times.keys())

    @property
    def has_redis(self) -> bool:
        return self._redis is not None and self._redis_key is not None

    def is_watching(self, key: str) -> bool:
        return key in self._busy_dict

    def init_update_times(self, update_times: Dict[str, datetime]):
        filtered_updates = {
            key: [value, None]
            for key, value in update_times.items()
            if self.is_watching(key) and value is not None
        }
        self._update_times = filtered_updates

    def is_busy(self, key: str) -> bool:
        return self._busy_dict.get(key, False)

    def set_busy(self, key: str, busy: bool):
        self._busy_dict[key] = busy

    def push(self, key: str, new_time: datetime):
        if key not in self._update_times:
            self._update_times[key] = [None, None]
        current_first = self._update_times[key][0]
        if current_first is None or new_time > current_first:
            self._update_times[key][0] = new_time
        else:
            self._update_times[key][1] = new_time

    def pop(self, key: str) -> Optional[ModifiedModel]:
        if key not in self.jobs:
            return None
        time_range = self.get(key)
        if time_range[0] is not None and time_range[1] is not None:
            modified_model = ModifiedModel(key=key, old_time=time_range[0], new_time=time_range[1])
            self.set(key, [time_range[1], None])
            return modified_model
        return None

    def set_job(self, key: str, job: Dict[str, Any]):
        self._job_dict[key] = job
        
    def get_job(self, key: str) -> Optional[Dict[str, Any]]:
        return self._job_dict.get(key, None)

    def pop_job(self, key: str) -> Optional[Dict[str, Any]]:
        job = self._job_dict.get(key, None)
        if key in self._job_dict:
            self._job_dict[key] = None
        return job

    def get(self, key: str) -> List[Optional[datetime]]:
        return self._update_times.get(key, [None, None])

    def set(self, key: str, time_range: List[Optional[datetime]]):
        self._update_times[key] = time_range

    def save_redis_update_time(self, modified_model: ModifiedModel) -> None:
        if not self.has_redis:
            return
        if modified_model.new_time is None:
            return
        try:
            self._redis.hset(
                self._redis_key,
                modified_model.key,
                DateUtils.format(modified_model.new_time, DATE_FORMAT.PRESION.value)
            )
        except Exception as e:
            logger.warning(f"Failed to save update time to Redis: {e}")
            
    def _start(self, sync: bool) -> None:
        if self._sync is not None and self._sync != sync:
            raise RuntimeError("Cannot start both async and sync schedulers.")
        self._sync = sync

    def start(self, *args, check_time: int = 300) -> None:
        """ 启动异步调度器 """
        io_loop = ioloop.IOLoop.current()
        if io_loop in self._io_loops:
            return
        self._io_loops[io_loop] = True
        if len(self._io_loops) > 1:
            io_loop.call_later(10, lambda: None)  # 非阻塞延迟
        loop_fn = functools.partial(self.loop, *args)
        self._scheduler = ioloop.PeriodicCallback(loop_fn, check_time)
        self._start(sync=False)
        self._scheduler.start()

    def loop(self, *args):
        """ 异步循环任务 """
        raise NotImplementedError()

    def sync_start(self, *args, check_time: int = 300) -> None:
        """ 启动同步调度器 """
        if self._scheduler is not None:
            return
        self._scheduler = functools.partial(self.sync_loop, *args)
        self._start(sync=True)
        while True:
            try:
                self._scheduler()
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user.")
                break
            except Exception as e:
                logger.error(f"JobStore loop error: {e}")
            sleep(check_time / 1000)

    def sync_loop(self, *args):
        """ 同步循环任务 """
        raise NotImplementedError()