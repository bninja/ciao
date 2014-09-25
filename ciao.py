"""
Simple resource throttling. Use it e.g. like:

.. code:: python

    import datetime

    import ciao
    import sqlalchemy as sa
    
    
    db_engine = create_engine('postgres://mikey:corleone@localhost/study')
    
    db_throttle = ciao.Throttle(
        duration=datetime.timedelta(seconds=30),
        cap=datetime.timedelta(minutes=10),
        backoff=2,
        exc=(
            sa.exc.OperationalError,
            sa.exc.DisconnectionError,
            sa.exc.InvalidRequestError,
            sa.exc.InterfaceError,
            sa.exc.DatabaseError,
            sa.exc.DBAPIError,
        ),
    )

    if not db_throttle:
        with db_throttle:
            db_engine.execute('SELECT * FROM slippers WHERE name = "mine"')

"""
__version__ = '0.1.0'

import contextlib
import datetime
import logging
import inspect
import time


logger = logging.getLogger(__name__)


class Throttle(object):

    exc = (RuntimeError,)

    def __init__(self, duration, backoff=0, cap=None, off=False, exc=None):
        self.off = off
        self.duration = self._as_delta(duration)
        self.backoff = backoff
        self.cap = self._as_delta(cap) if cap is not None else None
        self.count = 0
        self.expires_at = None
        self.exc = self._as_exc(exc or self.exc)

    @classmethod
    def _as_exc(cls, value):
        if inspect.isclass(value):
            if issubclass(value, Exception):
                return (value,)
            raise TypeError('{0!r} is not an Exception class'.format(value))
        if isinstance(value, (list, tuple)):
            for i, exc in enumerate(value):
                if not inspect.isclass(exc) or not issubclass(exc, Exception):
                    raise TypeError(
                        '{0!r}[{1}] is not an Exception class'.format(exc, i)
                    )
                return tuple(value)
        raise TypeError(
            '{0!r} is not an Exception class or sequence'.format(value)
        )

    @classmethod
    def _as_delta(self, value):
        if isinstance(value, (int, long, float)):
            return datetime.timedelta(seconds=value)
        elif isinstance(value, datetime.timedelta):
            return value
        raise TypeError(
            '{0!r} is not number of seconds or datetime.timedelta.'.format(value)
        )

    def reset(self, off=None):
        self.count = 0
        self.expires_at = None

    def __invert__(self):
        return not self.__bool__()

    def __bool__(self):
        return self.__nonzero__()

    def __nonzero__(self):
        if self.off:
            return True
        if not self.expires_at:
            return False
        if self.expires_at < time.time():
            self.expires_at = None
            return False
        return True

    def wait(self):
        if not self:
            return
        if self.off:
            raise Exception('Cannot wait forever.')
        duration = max(self.expires_at - time.time(), 0)
        logger.info('yielding for %s second(s)', duration)
        time.sleep(duration)

    def step(self, ex=None):
        duration = self.duration + self.duration * self.backoff * self.count
        if self.cap and duration > self.cap:
            duration = self.cap
        self.expires_at = time.time() + duration.seconds
        self.count += 1
        return duration

    def __call__(self, ex=None):
        return self.step(ex)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if isinstance(value, self.exc):
            self.step(value)

    @contextlib.contextmanager
    def guard(self):
        try:
            yield
        except self.exc as ex:
            # NOTE: log and depress throttle but suppress exception
            logger.exception(ex)
            self.step(ex)
