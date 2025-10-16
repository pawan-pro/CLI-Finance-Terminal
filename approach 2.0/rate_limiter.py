import time
import json
from collections import deque
from filelock import FileLock

class APITimer:
    """A class to manage API call rates across multiple processes to avoid exceeding limits."""
    def __init__(self, calls: int, period: int, file_path: str):
        self.calls = calls
        self.period = period
        self.file_path = file_path
        self.lock = FileLock(f"{self.file_path}.lock")

    def _read_timestamps(self) -> deque:
        try:
            with self.lock:
                with open(self.file_path, 'r') as f:
                    timestamps = json.load(f)
                    return deque(timestamps)
        except (FileNotFoundError, json.JSONDecodeError):
            return deque()

    def _write_timestamps(self, timestamps: deque):
        with self.lock:
            with open(self.file_path, 'w') as f:
                json.dump(list(timestamps), f)

    def wait_if_needed(self):
        """
        Checks timestamps of previous calls and waits if the rate limit
        is about to be breached.
        """
        timestamps = self._read_timestamps()

        # 1. Remove timestamps older than the specified period
        now = time.monotonic()
        while timestamps and timestamps[0] <= now - self.period:
            timestamps.popleft()

        # 2. If we have made the maximum number of calls, calculate wait time
        if len(timestamps) >= self.calls:
            wait_time = timestamps[0] - (now - self.period)
            if wait_time > 0:
                print(f"Rate limit reached. Waiting for {wait_time:.2f} seconds...")
                time.sleep(wait_time)

        # 3. Record the timestamp of the current call and write back to the file
        timestamps.append(time.monotonic())
        self._write_timestamps(timestamps)
