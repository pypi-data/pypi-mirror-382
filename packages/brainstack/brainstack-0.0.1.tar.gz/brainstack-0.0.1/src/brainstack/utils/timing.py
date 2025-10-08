import time
from typing import Dict, List

def now_ms() -> int:
    """Return current time as epoch milliseconds."""
    return int(time.time() * 1000)

class TimeBlock:
    """Context manager to measure execution time of a block."""
    def __init__(self, label: str):
        self.label = label
        self.start: float = 0.0
        self.result: Dict[str, str | int] = {}

    def __enter__(self) -> 'TimeBlock':
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        elapsed_ms = int((time.time() - self.start) * 1000)
        self.result = {"label": self.label, "ms": elapsed_ms}

def average_ms(samples: List[int]) -> float:
    """Calculate average of millisecond samples.

    Args:
        samples: List of millisecond measurements.

    Returns:
        Average in milliseconds; 0.0 if list is empty.
    """
    return sum(samples) / len(samples) if samples else 0.0

if __name__ == "__main__":
    # Test timing utilities
    with TimeBlock("sleep_test") as timer:
        time.sleep(0.05)  # Simulate work
    result = timer.result  # Access result after context

    # Test average_ms
    sample_times = [100, 200, 300]
    avg = average_ms(sample_times)
    print(f"Timed block result: {result}")
    print(f"Average of {sample_times}: {avg:.2f} ms")