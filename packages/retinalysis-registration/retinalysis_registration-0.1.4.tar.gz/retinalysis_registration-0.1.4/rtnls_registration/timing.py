import contextlib
import time
from typing import Optional


class TimingStats:
    times = {}

    def add_time(self, name: str, elapsed: float):
        self.times[name] = elapsed

    def __str__(self) -> str:
        lines = ["Timing Statistics:"]
        length = max(len(name) for name in self.times)
        for name, time in self.times.items():
            lines.append(f"{name:<{length}}: {time:.3f} s")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return str(self)


@contextlib.contextmanager
def timing(stats: Optional[TimingStats] = None, name: str = "operation"):
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        if stats is not None:
            stats.add_time(name, elapsed)
