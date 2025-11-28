"""Runtime loop for PLC program simulation."""

import time
from .program import Program


class Runtime:
    """Runtime loop for executing PLC programs."""

    def __init__(self, program: Program, target_scan_ms: int = 100):
        self.program = program
        self.target_scan_ms = target_scan_ms
        self._running = False

    def run(self, max_scans: int | None = None) -> None:
        """
        Run the PLC program for a specified number of scans or indefinitely.

        Args:
            max_scans: Maximum number of scans to execute. None for infinite.
        """
        self._running = True
        scan_count = 0
        prev_time = time.time() * 1000.0

        while self._running:
            now = time.time() * 1000.0
            dt_ms = int(now - prev_time)
            if dt_ms <= 0:
                dt_ms = self.target_scan_ms
            prev_time = now

            self.program.scan(dt_ms)

            scan_count += 1
            if max_scans is not None and scan_count >= max_scans:
                break

            # crude pacing
            time.sleep(self.target_scan_ms / 1000.0)

    def stop(self) -> None:
        """Stop the runtime loop."""
        self._running = False
