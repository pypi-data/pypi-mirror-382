"""A module containing a custom Lock and Semaphore class"""

import threading

class Lock():
    """
    Extends threading.Lock by allowing timeout to be None.

    threading.Lock cannot be subclassed as it is a factory function.
    https://stackoverflow.com/a/6781398
    """

    def __init__(self):
        self._lock = threading.Lock()

    def acquire(self, blocking: bool = True, timeout: float | None = None):
        """
        Try to acquire the Lock.

        If blocking is disabled, it doesn't wait for the timeout.

        If timeout is set, wait for n seconds before returning.
        """

        return self._lock.acquire(blocking, -1 if timeout is None else timeout)

    def locked(self) -> bool:
        """Returns whether the Lock is held"""

        return self._lock.locked()

    def release(self):
        """Release the lock if it is currently held"""

        self._lock.release()

    def __enter__(self):
        self.acquire()

    # keep signature the same as threading.Lock
    # pylint: disable-next=redefined-builtin
    def __exit__(self, type, value, traceback):
        self.release()

# we can't use the default threading.Semaphore
# because we need a semaphore with value == 0 if it isn't held
# This is the opposite behaviour of threading.Semaphore
class Semaphore(threading.BoundedSemaphore):
    """
    Extends threading.BoundedSemaphore by adding a locked() function.

    This makes it equivalent to threading.Lock method signature-wise.
    """

    _value: int
    _initial_value: int

    def locked(self) -> bool:
        """Returns whether the Semaphore is held at least once"""

        return self._value != self._initial_value
