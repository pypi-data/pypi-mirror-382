import threading
import time


class CooldownLock:
    def __init__(self, cooldown: float):
        self._lock = threading.Lock()
        self._cooldown = cooldown
        self._earliest_use_time = 0

    def acquire(self):
        self._lock.acquire()

        remaining_cooldown = self._earliest_use_time - time.monotonic()
        if remaining_cooldown > 0:
            time.sleep(remaining_cooldown)

    def release(self):
        if not self._lock.locked():
            raise RuntimeError("Lock not held")

        self._earliest_use_time = time.monotonic() + self._cooldown
        self._lock.release()

    def __enter__(self) -> "CooldownLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
