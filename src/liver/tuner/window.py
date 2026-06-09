from __future__ import annotations

import json
import signal
from typing import Any

from AnyQt.QtCore import QTimer
from AnyQt.QtGui import QFont
from AnyQt.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .config import LEARNER_SPECS, LearnerSpecs
from .runner import RunThread
from .ui_helpers import (
    format_duration,
    hline,
)
from .widgets import LearnerBlock, ParamBinding


class MethodSelectionError(Exception):
    """Raised when no method is selected."""
    pass

class ExperimentSelectionError(Exception):
    """Raised when no experiment is selected."""
    pass


class MainWindow(QWidget):
    def __init__(self, learner_specs: LearnerSpecs | None = None) -> None:
        super().__init__()
        self.learner_specs = learner_specs or LEARNER_SPECS
        self.param_bindings: dict[str, dict[str, ParamBinding]] = {}
        self.learner_blocks: dict[str, LearnerBlock] = {}
        self.run_thread: RunThread | None = None
        self.is_running = False
        self.is_cancelling = False

        self.setWindowTitle("Learner Parameter Tuner")
        self.setMinimumWidth(1180)

        self._build_ui()
        self._connect_signals()
        self._install_sigint_handler()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        toolbar = self._build_toolbar()
        main_layout.addWidget(toolbar)

        status_panel = self._build_status_panel()
        main_layout.addWidget(status_panel)

        main_layout.addWidget(hline(section=True))

        self.learner_container = self._build_learner_grid()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.learner_container)
        main_layout.addWidget(scroll_area, 1)

        # Initial update of toolbar learners count
        self.update_toolbar_learners_count()

        self.widgets_disabled_during_run = [
            self.btn_load,
            self.btn_save,
            self.rb_cv,
            self.rb_holdout,
            self.learner_container,
        ]

        self.setLayout(main_layout)
        self.resize(1240, 780)

    def _build_toolbar(self) -> QWidget:
        toolbar_widget = QWidget()
        toolbar_widget.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(16, 10, 16, 10)
        toolbar_layout.setSpacing(10)

        cfg_label = QLabel("Config")
        cfg_label.setObjectName("toolbar-label")
        toolbar_layout.addWidget(cfg_label)

        self.btn_load = QPushButton("⬆  Load")
        self.btn_load.setObjectName("btn-secondary")
        self.btn_load.setToolTip("Load a saved configuration from a JSON file")

        self.btn_save = QPushButton("⬇  Save")
        self.btn_save.setObjectName("btn-secondary")
        self.btn_save.setToolTip("Save the current configuration to a JSON file")

        toolbar_layout.addWidget(self.btn_load)
        toolbar_layout.addWidget(self.btn_save)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setObjectName("vline")
        sep1.setFixedHeight(28)
        toolbar_layout.addSpacing(6)
        toolbar_layout.addWidget(sep1)
        toolbar_layout.addSpacing(6)

        # Experiment section
        experiment_label = QLabel("Experiment")
        experiment_label.setObjectName("toolbar-label")
        toolbar_layout.addWidget(experiment_label)
        
        self.rb_1 = QRadioButton("Multiclass (1)")
        self.rb_1.setObjectName("method-radio")
        self.rb_1.setToolTip('Multiclass classification for Indian dataset')

        self.rb_2 = QRadioButton("Binary (2)")
        self.rb_2.setObjectName("method-radio")
        self.rb_2.setToolTip('Binary classification for Indian dataset')

        self.rb_3 = QRadioButton("Binary (3)")
        self.rb_3.setObjectName("method-radio")
        self.rb_3.setToolTip('Binary classification for all 3 datasets')
        
        self.experiment_group = QButtonGroup(self)
        self.experiment_group.addButton(self.rb_1, 0)
        self.experiment_group.addButton(self.rb_2, 1)
        self.experiment_group.addButton(self.rb_3, 2)

        toolbar_layout.addWidget(self.rb_1)
        toolbar_layout.addWidget(self.rb_2)
        toolbar_layout.addWidget(self.rb_3)
        toolbar_layout.addStretch()

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        sep2.setObjectName("vline")
        sep2.setFixedHeight(28)
        toolbar_layout.addSpacing(6)
        toolbar_layout.addWidget(sep2)
        toolbar_layout.addSpacing(6)

        # Method section
        method_label = QLabel("Method")
        method_label.setObjectName("toolbar-label")
        toolbar_layout.addWidget(method_label)

        self.method_group = QButtonGroup(self)
        self.rb_cv = QRadioButton("Cross validation")
        self.rb_cv.setObjectName("method-radio")
        self.rb_holdout = QRadioButton("Hold-out")
        self.rb_holdout.setObjectName("method-radio")
        self.method_group.addButton(self.rb_cv, 0)
        self.method_group.addButton(self.rb_holdout, 1)

        toolbar_layout.addWidget(self.rb_cv)
        toolbar_layout.addWidget(self.rb_holdout)
        toolbar_layout.addStretch()

        self.learners_count = QLabel("#Learners: 0")
        self.learners_count.setObjectName("toolbar-label")
        toolbar_layout.addWidget(self.learners_count)

        # Running section
        self.btn_run = QPushButton("▶  RUN")
        self.btn_run.setObjectName("btn-run")
        self.btn_run.setToolTip("Run with the current configuration")
        toolbar_layout.addWidget(self.btn_run)

        toolbar_widget.setLayout(toolbar_layout)
        return toolbar_widget

    def _build_status_panel(self) -> QWidget:
        status_panel = QWidget()
        status_panel.setObjectName("status-panel")
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(12)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status-label")
        self.status_label.setMinimumWidth(260)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")

        self.elapsed_label = QLabel("Elapsed: 00:00")
        self.elapsed_label.setObjectName("time-label")
        self.elapsed_label.setMinimumWidth(120)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar, 1)
        status_layout.addWidget(self.elapsed_label)
        status_panel.setLayout(status_layout)
        return status_panel

    def _build_learner_grid(self) -> QWidget:
        learner_container = QWidget()
        learner_layout = QVBoxLayout()
        learner_layout.setContentsMargins(0, 0, 0, 0)
        learner_layout.setSpacing(14)

        for r, learner in enumerate(LEARNER_SPECS.keys()):
            row = QHBoxLayout()
            row.setSpacing(14)
            learner_block = LearnerBlock(
                learner,
                self.learner_specs[learner],
                self.param_bindings,
                on_combinations_changed=self.update_toolbar_learners_count
            )
            row.addWidget(learner_block)
            self.learner_blocks[learner] = learner_block

            # Connect enable checkbox changes to update toolbar count
            learner_block.enable_checkbox.stateChanged.connect(self.update_toolbar_learners_count)

            row_widget = QWidget()
            row_widget.setLayout(row)
            learner_layout.addWidget(row_widget)

            if r < len(LEARNER_SPECS.keys()) - 1:
                learner_layout.addWidget(hline(section=True))

        learner_layout.addStretch()
        learner_container.setLayout(learner_layout)
        return learner_container

    # ------------------------------------------------------------------
    # Signals and runtime behavior
    # ------------------------------------------------------------------
    def _connect_signals(self) -> None:
        self.btn_load.clicked.connect(self.on_load)
        self.btn_save.clicked.connect(self.on_dump)
        self.btn_run.clicked.connect(self.on_run_clicked)

    def update_toolbar_learners_count(self) -> None:
        """Update the learners count in the toolbar based on current UI state."""
        try:
            cfg = self.collect_config()
            num_learners = self.get_enabled_learners_count(cfg)
            self.learners_count.setText(f"#Learners: {num_learners}")
        except ValueError:
            # Invalid JSON in manual inputs - show error state
            self.learners_count.setText("#Learners: invalid input")
        except Exception:
            # If config is incomplete, just don't update
            pass

    def _install_sigint_handler(self) -> None:
        signal.signal(signal.SIGINT, self.handle_sigint)

        # Qt needs a tiny timer so Python gets a chance to process SIGINT/Ctrl+C.
        self.signal_timer = QTimer(self)
        self.signal_timer.start(200)
        self.signal_timer.timeout.connect(lambda: None)

    def get_enabled_learners_count(self, cfg: dict[str, Any]) -> int:
        """Count total combinations only for enabled learners."""
        import math
        total = 0

        for learner_key, learner_info in cfg.get("learners", {}).items():
            # Skip disabled learners
            if not learner_info.get("enabled", True):
                continue

            params = learner_info.get("params", learner_info)
            from .runner import configured_values_for_sweep
            lengths = [len(configured_values_for_sweep(info)) for info in params.values()]
            learner_configs = math.prod(lengths) if lengths else 1
            total += learner_configs

        return max(1, total)

    def collect_config(self) -> dict[str, Any]:
        """Return current UI state. Parent keys are learner IDs and API parameter names."""

        if not (
            self.rb_1.isChecked() or
            self.rb_2.isChecked() or
            self.rb_3.isChecked()
        ):
            raise ExperimentSelectionError("Please select an experiment: Multiclass (1), Binary (2), or Binary (3).")
        elif not (
            self.rb_cv.isChecked() or
            self.rb_holdout.isChecked()
        ):
            raise MethodSelectionError("Please select an evaluation method: Cross validation or Hold-out.")

        cfg: dict[str, Any] = {
            "exprid": int(self.experiment_group.checkedId() + 1),
            "method": "cross-validation" if self.rb_cv.isChecked() else "hold-out",
            "learners": {},
        }

        for learner_key, params in self.param_bindings.items():
            learner_spec = self.learner_specs[learner_key]
            cfg["learners"][learner_key] = {
                "display_name": learner_spec.get("display_name", learner_key),
                "api_class": learner_spec.get("api_class"),
                "enabled": self.learner_blocks[learner_key].is_enabled(),
                "params": {},
            }

            for api_param_name, binding in params.items():
                cfg["learners"][learner_key]["params"][api_param_name] = binding.as_config()

        return cfg

    def apply_config(self, cfg: dict[str, Any]) -> None:
        """Apply a loaded config dict back to the UI widgets."""
        method = cfg.get("method")
        (self.rb_cv if method == "cross-validation" else self.rb_holdout).setChecked(True)

        for learner_key, learner_info in cfg.get("learners", {}).items():
            if learner_key not in self.param_bindings:
                continue

            # Restore enabled state
            if learner_key in self.learner_blocks:
                enabled = learner_info.get("enabled", True)
                self.learner_blocks[learner_key].enable_checkbox.setChecked(enabled)

            # Supports both the new nested shape and the older direct-param shape.
            params = learner_info.get("params", learner_info)

            for api_param_name, info in params.items():
                if api_param_name not in self.param_bindings[learner_key]:
                    continue

                binding = self.param_bindings[learner_key][api_param_name]
                mode = info.get("mode", "default")
                value = info.get("value", [binding.default_value])

                if mode == "manual":
                    binding.apply_value(value)
                    binding.apply_mode("manual")
                else:
                    binding.apply_mode("default")

                # Restore locked state
                locked = info.get("locked", False)
                binding.apply_locked(locked)

    def set_running_state(self, running: bool, *, cancelling: bool = False) -> None:
        self.is_running = running
        self.is_cancelling = cancelling

        for widget in self.widgets_disabled_during_run:
            widget.setEnabled(not running)

        if running:
            self.btn_run.setText("■  CANCEL" if not cancelling else "Cancelling...")
            self.btn_run.setEnabled(not cancelling)
        else:
            self.btn_run.setText("▶  RUN")
            self.btn_run.setEnabled(True)

    def on_load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Configuration", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                cfg = json.load(f)
            self.apply_config(cfg)
        except Exception as exc:
            QMessageBox.critical(self, "Load Error", f"Could not load configuration:\n{exc}")

    def on_dump(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Configuration", "config.json", "JSON Files (*.json)")
        if not path:
            return
        try:
            cfg = self.collect_config()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            QMessageBox.information(self, "Saved", f"Configuration saved to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", f"Could not save configuration:\n{exc}")

    def on_progress(self, current: int, total: int, elapsed: float, remaining: float | None, message: str) -> None:
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(current)
        percent = int((current / total) * 100) if total else 0
        self.progress_bar.setFormat(f"{percent}%  ({current}/{total})")

        self.elapsed_label.setText(f"Elapsed: {format_duration(elapsed)}")
        self.status_label.setText(message)

    def cleanup_thread(self) -> None:
        self.run_thread = None

    def on_finished(self, success: bool, message: str) -> None:
        self.set_running_state(False)
        self.status_label.setText(message)

        if success:
            QMessageBox.information(self, "Run", message)
        else:
            QMessageBox.warning(self, "Run", message)

    def start_run(self) -> None:
        try:
            cfg = self.collect_config()
        except ExperimentSelectionError as exc:
            QMessageBox.critical(self, "Experiment not selected", str(exc))
            return
        except MethodSelectionError as exc:
            QMessageBox.critical(self, "Method not selected", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Invalid configuration", str(exc))
            return

        num_learners = self.get_enabled_learners_count(cfg)
        self.progress_bar.setRange(0, num_learners)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat(f"0%  (0/{num_learners})")
        self.elapsed_label.setText("Elapsed: 00:00")
        self.status_label.setText("Starting run...")

        self.set_running_state(True)

        self.learners_count.setText(f"#Learners: {num_learners}")

        self.run_thread = RunThread(cfg)
        self.run_thread.progress_changed.connect(self.on_progress)
        self.run_thread.run_finished.connect(self.on_finished)
        self.run_thread.finished.connect(self.cleanup_thread)
        self.run_thread.start()

    def cancel_run(self, reason: str = "Cancellation requested...") -> None:
        if not self.is_running or self.run_thread is None:
            return
        self.status_label.setText(reason)
        self.set_running_state(True, cancelling=True)
        self.run_thread.cancel()

    def on_run_clicked(self) -> None:
        if self.is_running:
            self.cancel_run()
        else:
            self.start_run()

    def handle_sigint(self, signum, frame) -> None:  # noqa: ANN001, ARG002
        """Handle Ctrl+C from the terminal without leaving the worker half-running."""
        if self.is_running:
            self.cancel_run("Ctrl+C received. Cancelling safely...")
        else:
            QApplication.quit()
