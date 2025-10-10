import asyncio
import time
from leafsdk import logger

class MissionClock:
    def __init__(self, rate_hz: float):
        self._interval = 1.0 / rate_hz
        self._last_tick_time = None

    def tick(self):
        self._last_tick_time = time.time()

    def _compute_sleep_duration(self):
        elapsed = time.time() - self._last_tick_time
        return max(0.0, self._interval - elapsed)

    async def tock(self, blocking: bool = True):
        """
        Wait until the next mission cycle.  
        - If blocking=True → uses time.sleep() (sync, blocking)
        - If blocking=False → uses await asyncio.sleep() (non-blocking)
        """
        sleep_duration = self._compute_sleep_duration()

        if blocking:
            # 🔒 Blocks current thread
            time.sleep(sleep_duration)
        else:
            # 🚀 Yields back to event loop
            await asyncio.sleep(sleep_duration)