import time
from collections import deque

class APITimer:
    """A class to manage API call rates to avoid exceeding limits."""
    def __init__(self, calls: int, period: int):
        self.calls = calls  # Max number of calls
        self.period = period  # Time period in seconds
        self.timestamps = deque()

    def wait_if_needed(self):
        """
        Checks timestamps of previous calls and waits if the rate limit
        is about to be breached.
        """
        # 1. Remove timestamps older than the specified period
        now = time.monotonic()
        while self.timestamps and self.timestamps[0] <= now - self.period:
            self.timestamps.popleft()

        # 2. If we have made the maximum number of calls, calculate wait time
        if len(self.timestamps) >= self.calls:
            wait_time = self.timestamps[0] - (now - self.period)
            if wait_time > 0:
                print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        # 3. Record the timestamp of the current call
        self.timestamps.append(time.monotonic())
