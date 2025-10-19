"""Top-level ml_monitor shim for backward compatibility.

Some modules import `from ml_monitor import MLMonitor` (top-level).
This shim tries to re-export the implementation from
`ML_based_detectionn.ml_monitor` when available, otherwise defines a
minimal local fallback. This keeps tests and runtime imports stable.
"""
try:
    # Prefer the packaged implementation if present
    from ML_based_detectionn.ml_monitor import MLMonitor  # type: ignore
except Exception:
    # Fallback minimal implementation
    import time
    import logging
    from typing import Optional, Dict, Any

    class MLMonitor:
        def __init__(self):
            self._start_time: Optional[float] = None
            self.metadata: Dict[str, Any] = {}

        def start_analysis(self):
            self._start_time = time.time()
            logging.debug("ml_monitor shim: started at %s", self._start_time)

        def stop_analysis(self):
            if self._start_time is None:
                return None
            elapsed = time.time() - self._start_time
            self._start_time = None
            logging.debug("ml_monitor shim: stopped, elapsed=%.4fs", elapsed)
            return elapsed

        def record(self, key: str, value: Any):
            self.metadata[key] = value

        def get_metadata(self) -> Dict[str, Any]:
            return dict(self.metadata)
