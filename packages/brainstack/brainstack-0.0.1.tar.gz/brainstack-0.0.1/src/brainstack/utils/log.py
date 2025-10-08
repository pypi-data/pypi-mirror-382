import time
import datetime
import json
from typing import Dict, Any, List

# Module-level flag for controlling log printing
_PRINT_TO_STDOUT: bool = True

class Timer:
    """Context manager to measure execution time in milliseconds."""
    def __init__(self):
        self.ms: int = 0
        self._start: float = 0.0

    def __enter__(self) -> 'Timer':
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.ms = int((time.time() - self._start) * 1000)

def seed_info(seed: int) -> Dict[str, Any]:
    """Create a log entry with seed and current UTC timestamp.

    Args:
        seed: Integer seed for deterministic operations.

    Returns:
        Dict with seed and ISO8601 UTC timestamp.
    """
    return {
        "event": "seed_info",
        "seed": seed,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

def log_event(event: str, **fields) -> Dict[str, Any]:
    """Create a structured log entry with event name and fields.

    Args:
        event: Name of the event.
        **fields: Arbitrary key-value pairs to include in log.

    Returns:
        JSON-serializable dict with event, timestamp, and fields.
    """
    log_row = {
        "event": event,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        **fields
    }
    if _PRINT_TO_STDOUT:
        print(json.dumps(log_row, ensure_ascii=False))
    return log_row

def configure_logging(print_to_stdout: bool = True) -> None:
    """Configure whether logs are printed to stdout.

    Args:
        print_to_stdout: If True, logs are printed; if False, logs are silent.
    """
    global _PRINT_TO_STDOUT
    _PRINT_TO_STDOUT = print_to_stdout

def merge_logs(*rows) -> List[Dict[str, Any]]:
    """Flatten and filter non-None log rows into a list.

    Args:
        *rows: Variable number of log dicts or None.

    Returns:
        List of non-None log dictionaries.
    """
    return [row for row in rows if row is not None]

if __name__ == "__main__":
    # Test logging utilities
    configure_logging(True)  # Ensure printing is on for test
    seed_log = seed_info(42)
    event_log = log_event("test_event", status="success", value=123)

    # Test Timer
    with Timer() as t:
        time.sleep(0.1)  # Simulate work
    timer_log = log_event("timer_test", duration_ms=t.ms)

    # Test merge_logs
    merged = merge_logs(seed_log, event_log, None, timer_log)
    print(f"Merged logs count: {len(merged)}")
    print(f"Sample log: {json.dumps(merged[0], ensure_ascii=False)}")