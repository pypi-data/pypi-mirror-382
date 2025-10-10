"""Module containing the NamedLock and NamedSemaphore classes"""

from __future__ import annotations

import functools
import traceback
from datetime import datetime
from time import sleep

from abllib import error, log
from abllib._storage import InternalStorage
from abllib.wrapper._deprecated import deprecated
from abllib.wrapper._lock import Lock, Semaphore

logger = log.get_logger("LockWrapper")

class _BaseNamedLock():
    """
    The base class for the NamedLock and NamedSemaphore classes.
    """

    def __init__(self, lock_name: str, timeout: int | float | None = None):
        if isinstance(timeout, int):
            timeout = float(timeout)

        # TODO: add type validation
        if not isinstance(lock_name, str):
            raise error.WrongTypeError.with_values(lock_name, str)
        if not isinstance(timeout, float) and timeout is not None:
            raise error.WrongTypeError.with_values(timeout, (float, None))

        self._name = lock_name
        self._timeout = timeout

        if "_locks" not in InternalStorage:
            InternalStorage["_locks.global"] = Lock()
        self._allocation_lock: Lock = InternalStorage["_locks.global"]

    _name: str
    _lock: Lock | Semaphore
    _timeout: float | None
    _allocation_lock: Lock
    _other_lock: _BaseNamedLock | None = None

    @property
    def name(self) -> str:
        """Return the lock's name"""

        return self._name

    def acquire(self) -> None:
        """Acquire the lock, or throw an LockAcquisitionTimeoutError if timeout is not None"""

        if self._timeout is None:
            self._allocation_lock.acquire()

            # ensure the other lock is not held
            other = self._get_other()
            if other is not None:
                while other.locked():
                    sleep(0.025)

            if not self._lock.acquire():
                self._allocation_lock.release()
                raise error.LockAcquisitionTimeoutError()

            self._allocation_lock.release()
            return

        initial_time = datetime.now()
        if not self._allocation_lock.acquire(timeout=self._timeout):
            raise error.LockAcquisitionTimeoutError(error.INTERNAL)

        elapsed_time = (datetime.now() - initial_time).total_seconds()

        # ensure the other lock is not held
        other = self._get_other()
        if other is not None:
            while other.locked():
                sleep(0.025)
                elapsed_time += 0.025
                if elapsed_time > self._timeout:
                    self._allocation_lock.release()
                    raise error.LockAcquisitionTimeoutError()

        if not self._lock.acquire(timeout=self._timeout - elapsed_time):
            self._allocation_lock.release()
            raise error.LockAcquisitionTimeoutError()

        self._allocation_lock.release()

    def release(self) -> None:
        """Release the lock"""

        self._lock.release()

    def locked(self) -> bool:
        """Return whether the lock is currentyl held"""

        return self._lock.locked()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __call__(self, func):
        """Called when instance is used as a decorator"""

        def wrapper(*args, **kwargs):
            """The wrapped function that is called on function execution"""

            with self:
                ret = func(*args, **kwargs)

            return ret

        # https://stackoverflow.com/a/17705456/15436169
        functools.update_wrapper(wrapper, func)

        return wrapper

    def _get_other(self) -> _BaseNamedLock | None:
        raise NotImplementedError()

class NamedLock(_BaseNamedLock):
    """
    Make a function require a lock to be held during execution.

    Only a single NamedLock can hold the lock, but only if the NamedSemaphore is not currently held.

    Optionally provide a timeout in seconds,
    after which an LockAcquisitionTimeoutError is thrown (disabled if timeout is None).
    """

    def __init__(self, lock_name, timeout = None):
        super().__init__(lock_name, timeout)

        if f"_locks.{lock_name}.l" not in InternalStorage:
            InternalStorage[f"_locks.{lock_name}.l"] = Lock()

        self._lock = InternalStorage[f"_locks.{lock_name}.l"]

    def acquire(self):
        _log_callstack(f"NamedLock '{self.name}' was acquired here:")
        return super().acquire()

    def release(self):
        _log_callstack(f"NamedLock '{self.name}' was released here:")
        return super().release()

    def _get_other(self):
        if self._other_lock is not None:
            return self._other_lock

        if f"_locks.{self.name}.s" in InternalStorage:
            self._other_lock = InternalStorage[f"_locks.{self.name}.s"]
            return self._other_lock

        return None

class NamedSemaphore(_BaseNamedLock):
    """
    Make a function require a lock to be held during execution.

    Multiple NamedSemaphores can hold the same lock concurrently, but only if the NamedLock is not currently held.

    Optionally provide a timeout in seconds,
    after which an LockAcquisitionTimeoutError is thrown (disabled if timeout is None).
    """

    def __init__(self, lock_name, timeout = None):
        super().__init__(lock_name, timeout)

        if f"_locks.{lock_name}.s" not in InternalStorage:
            InternalStorage[f"_locks.{lock_name}.s"] = Semaphore(999)

        self._lock = InternalStorage[f"_locks.{lock_name}.s"]

    def acquire(self):
        _log_callstack(f"NamedSemaphore '{self.name}' was acquired here:")
        return super().acquire()

    def release(self):
        _log_callstack(f"NamedSemaphore '{self.name}' was released here:")
        return super().release()

    def _get_other(self):
        if self._other_lock is not None:
            return self._other_lock

        if f"_locks.{self.name}.l" in InternalStorage:
            self._other_lock = InternalStorage[f"_locks.{self.name}.l"]
            return self._other_lock

        return None

def _log_callstack(message: str):
    """Log the current callstack"""

    if log.get_loglevel() != log.LogLevel.ALL:
        return

    traces = traceback.format_list(traceback.extract_stack())
    traces.reverse()

    for line in traces:
        ignore = False
        for filename in ["_lock_wrapper.py", "_persistent_storage.py", "_volatile_storage.py", "_storage_view.py"]:
            if filename in line:
                ignore = True

        if not ignore:
            logger.debug(message + "\n" + line.strip())
            return

@deprecated
class WriteLock(NamedLock):
    """Deprecated alias for NamedLock"""

@deprecated
class ReadLock(NamedSemaphore):
    """Deprecated alias for NamedSemaphore"""
