from __future__ import annotations

import itertools
import math
import threading
import time
from typing import Any

from AnyQt.QtCore import QThread, Signal


def configured_values_for_sweep(info: dict[str, Any]) -> list[Any]:
    """
    Default mode gives one value. Manual mode gives many values.

    Important example:
    - default hidden_layer_sizes = [100] means one configuration: [100]
    - manual hidden_layer_sizes = [[100], [50, 50]] means two configurations
    """
    if info["mode"] == "manual":
        return info["value"]
    return [info["value"]]


def total_learners(cfg: dict[str, Any]) -> int:
    total = 0

    for learner_info in cfg.get("learners", {}).values():
        # Skip disabled learners
        if not learner_info.get("enabled", True):
            continue

        params = learner_info.get("params", learner_info)
        lengths = [len(configured_values_for_sweep(info)) for info in params.values()]
        learner_configs = math.prod(lengths) if lengths else 1
        total += learner_configs

    return max(1, total)


class RunThread(QThread):
    """
    Worker thread with no QWidget/QObject children.

    Rule of thumb:
    - worker thread may compute and emit signals;
    - main thread updates widgets;
    - do not create, edit, parent, or delete UI widgets here.
    """

    progress_changed = Signal(int, int, float, object, str)
    run_finished = Signal(bool, str)

    def __init__(self, cfg: dict[str, Any]):
        super().__init__()
        self.cfg = cfg
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        self._cancel_event.set()

    def run(self) -> None:
        exprid = self.cfg['exprid']
        method = self.cfg['method']

        learners: dict[str, list[dict[Any, Any]]] = {}
        for learner_key, learner_info in self.cfg.get("learners", {}).items():
            # Skip disabled learners
            if not learner_info.get("enabled", True):
                continue

            params = learner_info.get("params", {})

            param_names = list(params.keys())
            sweep_values = [configured_values_for_sweep(params[p]) for p in param_names]

            for combo in itertools.product(*sweep_values):
                learner_kwargs = dict(zip(param_names, combo, strict=True))
                learners[learner_key] = learners.get(learner_key, [])
                learners[learner_key].append(learner_kwargs)

        try:
            from liver.experiment import train

            start_time = time.monotonic()
            total = total_learners(self.cfg)
            current = [0]  # Use list to allow modification in nested function

            def timer_thread() -> None:
                """Background thread that emits elapsed time updates every 100ms."""
                while not self._cancel_event.is_set():
                    elapsed = time.monotonic() - start_time
                    self.progress_changed.emit(current[0], total, elapsed, None, 'PROGRESS')
                    time.sleep(0.1)

            # Start timer thread
            timer = threading.Thread(target=timer_thread, daemon=True)
            timer.start()

            def progress_callback(current_count: int, total_count: int, progress: float) -> None:
                current[0] = current_count
                elapsed = time.monotonic() - start_time
                self.progress_changed.emit(current_count, total_count, elapsed, None, 'PROGRESS')

            train(exprid, method, learners, progress_callback=progress_callback)
            self._cancel_event.set()  # Stop timer thread
            self.run_finished.emit(True, "Run finished successfully.")
        except Exception as exc:  # pragma: no cover - shown in GUI during normal use
            self._cancel_event.set()  # Stop timer thread
            self.run_finished.emit(False, f"Run failed: {exc}")
