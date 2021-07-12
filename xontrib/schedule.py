import builtins
import threading
import sched
import time
import schedule as _schedule
import datetime
import pause

__all__ = ()
__version__ = '0.0.1'

Inf = float('inf')


class SchedJob:
    def __init__(self, method, amount):
        self._method = method
        self._amount = amount

    def do(self, func, *pargs, **kwargs):
        self._method(self._amount, 0, func, pargs, kwargs)


class Scheduler:
    def __init__(self):
        self._thread = threading.Thread(daemon=True, name="scheduler", target=self._run)
        self.sched = sched.scheduler(time.time, pause.seconds)
        self._thread.start()

    def _run(self):
        while True:
            _schedule.run_pending()

            nextsched = self.sched.run(False)
            if nextsched is None:
                nextsched = Inf

            try:
                nextschedule = _schedule.idle_seconds()
            except Exception:
                nextschedule = Inf
            if nextschedule is None:
                nextschedule = Inf

            if nextsched == nextschedule == Inf:
                self._delay(1)  # Finish init
            else:
                self._delay(min(nextsched, nextschedule))

    def every(self, *pargs):
        return _schedule.every(*pargs)

    def when(self, when):
        if isinstance(when, datetime.datetime):
            when = when.timestamp()
        return SchedJob(self.sched.enterabs, when)

    def delay(self, delay):
        if isinstance(delay, datetime.timedelta):
            delay = delay.total_seconds()
        return SchedJob(self.sched.enter, delay)

    MAX_WAIT = 60

    def _delay(self, amount):
        pause.seconds(amount)


builtins.schedule = Scheduler()
