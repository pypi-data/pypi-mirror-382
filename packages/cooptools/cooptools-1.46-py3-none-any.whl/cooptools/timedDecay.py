import time
from typing import Optional
import logging
import math
from cooptools.decay import UniformDecay

logger = logging.getLogger(f'cooptools.timers')

class TimedDecay:
    def __init__(self,
                 time_ms: int,
                 init_value: float = None,
                 start_perf: float = None):
        self.time_ms = time_ms
        self.start_perf = None
        self.decay_function = UniformDecay(ms_to_zero=time_ms, init_value=init_value)

        if start_perf is not None:
            self.set_start(start_perf)

    def set_start(self, at_time):
        self.start_perf = at_time

    def check(self, at_time) -> Optional[float]:
        if self.start_perf is None:
            return None
        t = at_time - self.start_perf

        return self.decay_function.val_at_t(at_time)

    @property
    def EndTime(self):
        if not self.start_perf:
            return None

        return self.start_perf + self.time_ms / 1000

    def progress_at_time(self, at_time):
        if not self.start_perf:
            return None

        return min((at_time - self.start_perf) / (self.EndTime - self.start_perf), 1)

    def progress_val(self, at_time):
        if not self.start_perf:
            return None

        return self.decay_function.progress_at_time(at_time)

    def time_until_zero_ms(self, at_time):
        return self.time_ms * (1 - self.progress_at_time(at_time))

from cooptools.asyncable import Asyncable
import uuid
from typing import Callable
from multiprocessing import Process

class Timer:
    def __init__(self,
                 time_ms: int,
                 id: str = None,
                 start_on_init: bool = False,
                 as_async: bool = False,
                 reset_on_end: bool = False,
                 on_ended_callback: Callable = None,
                 callback_timeout_ms: int = None
                 ):
        self._id = id if id else str(uuid.uuid4())
        self._time_ms = time_ms
        # self._decayer: Optional[TimedDecay] = None
        self._start_thread_on_init = start_on_init
        self._started = start_on_init
        self._accumulated_ms = 0
        self._last_update = None
        self._reset_on_end = reset_on_end
        self._on_ended_callback = on_ended_callback
        self._callback_timeout_ms = callback_timeout_ms
        self._asyncable = Asyncable(
            loop_callback=self.update,
            start_on_init=True,
            as_async=as_async
        )


    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def reset(self, start: bool = False):
        logger.info(f"Resetting timer {self._id} to {self.TimeMs}ms...")
        self._accumulated_ms = 0

        if start:
            self.start()

    @property
    def TimeMs(self) -> int:
        return self._time_ms

    @property
    def AccummulatedMs(self) -> int:
        return self._accumulated_ms

    @property
    def MsRemaining(self) -> int:
        return max(0, self._time_ms - self.AccummulatedMs)

    @property
    def Finished(self) -> bool:
        return math.isclose(self.MsRemaining, 0)

    def update(self, delta_ms: int = None):
        if not self._started:
            return

        now = time.perf_counter() * 1000
        if delta_ms is None:
            delta_ms = now - self._last_update if self._last_update is not None else 0

        self._accumulated_ms += delta_ms
        logger.debug(f"timer {self._id} update() ran at {now} and has {int(self.MsRemaining)}ms remaining")
        self._last_update = now

        if self.MsRemaining == 0:
            self._handle_ended()

    def _handle_ended(self):
        logger.info(f"{self._time_ms}ms timer {self._id} ended at {self._last_update}.")

        if self._on_ended_callback is not None:
            self._handle_callback()

        if self._reset_on_end:
            self.reset(start=True)
        else:
            self.stop()

    def _handle_callback(self):
        t0 = time.perf_counter()
        logger.info(f"Executing callback from timer {self._id}")
        self._on_ended_callback()
        t1 = time.perf_counter()
        span = t1 - t0
        logger.info(f'callback on timer {self._id} finishes in {span * 1000}ms!')



class TimeTracker:
    def __init__(self):
        self._first = time.perf_counter()
        self._now = self._first
        self._last = self._first
        self._delta = None
        self._n_updates = 0

    def update(self,
               perf: int = None,
               delta_ms: int = None):
        self._last = self._now
        self._n_updates += 1
        self._now = None
        if perf:
            self._now = perf
        elif delta_ms is not None:
            self._now = self._last + delta_ms / 1000.0
        else:
            self._now = time.perf_counter()
        self._delta = self._now - self._last

    def adjusted_delta_ms(self, time_scale_seconds_per_second: int = 1):
        return self.Delta_S * time_scale_seconds_per_second * 1000

    def accrued_s(self, time_scale_seconds_per_second: int = 1):
        return self.Duration_S * time_scale_seconds_per_second * 1000

    @property
    def Now(self):
        return self._now

    @property
    def Last(self):
        return self._last

    @property
    def Duration_S(self):
        return self._now - self._first

    @property
    def Delta_S(self):
        return self._delta if self._delta is not None else 0

    @property
    def Delta_MS(self):
        return self.Delta_S * 1000

    @property
    def Avg_Update_MS(self):
        return (self._now - self._first) / self._n_updates * 1000



if __name__ == "__main__":
    start = time.perf_counter()

    timer = Timer(3000, start_on_init=True, as_async=True, reset_on_end=True, on_ended_callback=lambda: logging.info(f"Hey"), callback_timeout_ms=500)
    logging.basicConfig(level=logging.INFO)

    time.sleep(10)



    #
    # has_reset = False
    # while True:
    #     print(timeTracker.finished)
    #     time.sleep(.5)
    #     if time.perf_counter() - start > 10 and not has_reset:
    #         timeTracker.reset()
    #         has_reset = True
    #         print("reset")
    #
