import builtins
import threading
import sched
import time
import schedule as _schedule
import signal
import datetime

__all__ = ()
__version__ = '0.0.1'


class AbstractScheduler:
    def __init__(self):
        self._thread = threading.Thread(daemon=True, name="scheduler", target=self._run)
        self.sched = sched.scheduler(time.time, time.sleep)
        self._thread.start()

    def _run(self):
        while True:
            _schedule.run_pending()

            nextsched = self.sched.run(False)
            if nextsched is None:
                nextsched = float('inf')

            try:
                nextschedule = _schedule.idle_seconds()
            except Exception:
                nextschedule = float('inf')

            if nextsched == nextschedule == float('inf'):
                self._delay(1)  # Finish init
            else:
                self._delay(min(nextsched, nextschedule))

    def every(self):
        return _schedule.every()

    def when(self, when, func, *pargs, **kwargs):
        if isinstance(when, datetime.datetime):
            when = when.timestamp()
        self.sched.enterabs(when, 0, func, pargs, kwargs)

    def delay(self, delay, func, *pargs, **kwargs):
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()
        self.sched.enter(delay, 0, func, pargs, kwargs)


class SleepScheduler(AbstractScheduler):
    MAX_WAIT = 60

    def _delay(self, amount):
        time.sleep(max(amount, self.MAX_WAIT))


class PosixTimerScheduler(AbstractScheduler):
    def _delay(self, amount):
        time.sleep(max(amount, self.MAX_WAIT))


if hasattr(signal, 'setitimer'):
    builtins.schedule = SleepScheduler()
else:
    builtins.schedule = SleepScheduler()
