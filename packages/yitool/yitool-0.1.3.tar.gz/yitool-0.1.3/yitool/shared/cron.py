from typing import List
from croniter import croniter
from datetime import datetime
from yitool.enums import REPEAT_TYPE
    

class Cron(object):
    _base_time: datetime
    _repeat_type: REPEAT_TYPE
    
    def __init__(self, base_time: datetime, repeat_type: REPEAT_TYPE):
        if not isinstance(base_time, datetime):
            raise TypeError("base_time must be a datetime instance")
        if repeat_type not in REPEAT_TYPE:
            raise ValueError(f"Invalid repeat_type: {repeat_type}")
        self._base_time = base_time
        self._repeat_type = repeat_type
        self._iter = None
        
    @property
    def crontab_idxs(self) -> List[int]:
        idx_map = {
            REPEAT_TYPE.MINUTE: [0, 1, 2, 3, 4],
            REPEAT_TYPE.HOUR: [1, 2, 3, 4],
            REPEAT_TYPE.DAY: [2, 3, 4],
            REPEAT_TYPE.WEEK: [2, 3],
            REPEAT_TYPE.MONTH: [3, 4],
            REPEAT_TYPE.YEAR: [4],
        }
        return idx_map.get(self._repeat_type, -1)
        
    @property
    def base_time(self) -> datetime:
        return self._base_time
        
    @property
    def crontab(self) -> str:            
        year = self.base_time.year
        month = self.base_time.month
        day = self.base_time.day
        weekday = self.base_time.weekday()
        hour = self.base_time.hour
        minute = self.base_time.minute
        arr = [str(int_val) for int_val in [minute, hour, day, month, weekday]]
        for idx in self.crontab_idxs:
            arr[idx] = '*'
        return ' '.join(arr)
    
    def get_next(self, dt: datetime = None) -> datetime:
        if dt is not None:
            if not isinstance(dt, datetime):
                raise TypeError("dt must be a datetime instance")
            self._base_time = dt
            # Reset iterator when base time changes
            self._iter = None
        if self._iter is None:
            try:
                self._iter = croniter(self.crontab, self.base_time)
            except Exception as e:
                raise RuntimeError(f"Failed to create cron iterator with crontab '{self.crontab}'") from e
        return self._iter.get_next(datetime)
    

if __name__ == '__main__':
    for repeat_type in REPEAT_TYPE:
        cron = Cron(datetime.now(), repeat_type=repeat_type)
        print(repeat_type, cron.crontab)
        for _ in range(5):
            print(repeat_type, cron.get_next())