from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from AnyQt.QtCore import QSize, Qt
from AnyQt.QtGui import QIcon, QPainter, QPen, QPixmap
from AnyQt.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from loguru import logger

from .ui_helpers import hline, json_text, parse_manual_list, vline


def create_lock_icon(locked: bool, size: int = 32) -> QIcon:
    """Create a lock or unlock icon using QPainter.

    Args:
        locked: If True, draw a closed lock; if False, draw an open lock.
        size: Icon size in pixels.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw lock body (rectangle)
    body_x = size * 0.25
    body_y = size * 0.55
    body_w = size * 0.5
    body_h = size * 0.35
    painter.setPen(QPen(Qt.GlobalColor.black, max(1, size // 16)))
    painter.drawRect(int(body_x), int(body_y), int(body_w), int(body_h))

    if locked:
        # Draw closed shackle (arch over the lock body)
        shackle_x = size * 0.35
        shackle_y = size * 0.15
        shackle_w = size * 0.3
        shackle_h = size * 0.35
        painter.drawArc(int(shackle_x), int(shackle_y), int(shackle_w), int(shackle_h), 0, 180 * 16)
    else:
        # Draw open shackle (left arc, open to the right)
        shackle_x = size * 0.25
        shackle_y = size * 0.15
        shackle_w = size * 0.2
        shackle_h = size * 0.35
        painter.drawArc(int(shackle_x), int(shackle_y), int(shackle_w), int(shackle_h), 0, 180 * 16)

    painter.end()
    return QIcon(pixmap)


@dataclass
class ParamBinding:
    learner_key: str
    learner_display_name: str
    api_param_name: str
    spec: dict[str, Any]
    manual_input: QLineEdit
    btn_group: QButtonGroup
    default_label: QLabel
    lock_button: QPushButton = None

    @property
    def default_value(self) -> Any:
        return self.spec["default"]

    def mode(self) -> str:
        return "manual" if self.btn_group.checkedId() == 1 else "default"

    def value(self) -> Any:
        if self.mode() == "default":
            return self.default_value
        return parse_manual_list(
            self.manual_input.text(),
            learner_name=self.learner_key,
            param_name=self.api_param_name,
        )

    def selected_values_for_sweep(self) -> list[Any]:
        if self.is_locked():
            # Locked parameters use their current value (fixed, not swept)
            return [self.value()]
        if self.mode() == "manual":
            return self.value()
        return [self.default_value]

    def is_locked(self) -> bool:
        """Check if this parameter is locked from sweeping."""
        if self.lock_button is None:
            return False
        return self.lock_button.isChecked()

    def as_config(self) -> dict[str, Any]:
        """Serializable state. The key in the parent dict remains the API name."""
        return {
            "mode": self.mode(),
            "value": self.value(),
            "api_param": self.api_param_name,
            "orange": self.spec.get("orange"),
            "type": self.spec.get("type", "unknown"),
            "locked": self.is_locked(),
        }

    def apply_mode(self, mode: str) -> None:
        is_manual = mode == "manual"
        self.btn_group.button(1 if is_manual else 0).setChecked(True)
        self.default_label.setEnabled(not is_manual)
        self.manual_input.setEnabled(is_manual)

    def apply_value(self, value: Any) -> None:
        # Manual value must be a list. If a scalar is loaded from an old config,
        # wrap it so the UI still works.
        if isinstance(value, list):
            self.manual_input.setText(json_text(value))
        else:
            self.manual_input.setText(json_text([value]))

    def apply_locked(self, locked: bool) -> None:
        """Restore locked state when loading a config."""
        if self.lock_button is not None:
            self.lock_button.setChecked(locked)
            self.lock_button.setIcon(create_lock_icon(locked=locked))


class Header(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("section-header")

        # Column 1 - parameter labels
        param = QLabel("Parameter")
        param.setObjectName("section-label")
        param.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col1 = QHBoxLayout()
        col1.setContentsMargins(8, 0, 8, 0)
        col1.addWidget(param)

        # Column 2 - fields
        field = QLabel("Field")
        field.setObjectName("section-label")
        field.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col2 = QHBoxLayout()
        col2.setContentsMargins(8, 0, 8, 0)
        col2.addWidget(field)

        # Column 3 - default values
        defaults = QLabel("Default values")
        defaults.setObjectName("section-label")
        defaults.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col3 = QHBoxLayout()
        col3.setContentsMargins(8, 0, 8, 0)
        col3.addWidget(defaults)

        # Column 4 - manual values
        manuals = QLabel("Manual values")
        manuals.setObjectName("section-label")
        manuals.setAlignment(Qt.AlignmentFlag.AlignCenter)

        col4 = QHBoxLayout()
        col4.setContentsMargins(8, 0, 8, 0)
        col4.addWidget(manuals)

        # Whole box
        first = QWidget()
        first.setLayout(col1)

        second = QWidget()
        second.setLayout(col2)

        third = QWidget()
        third.setLayout(col3)

        fourth = QWidget()
        fourth.setLayout(col4)

        # Whole box
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        row.addWidget(first, 2)
        row.addWidget(vline())
        row.addWidget(second, 1)
        row.addWidget(vline())
        row.addWidget(third, 1)
        row.addWidget(vline())
        row.addWidget(fourth, 2)


class ParamBlock(QWidget):
    def __init__(
        self,
        api_param_name: str,
        spec: dict[str, Any],
        *,
        field: bool = False,
        parent=None,
    ):
        super().__init__(parent)

        display_label = spec.get("orange", "-")

        label_text = api_param_name if field else display_label
        label = QLabel(label_text)
        label.setObjectName("param-name")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setToolTip(spec.get("description", ""))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(label)
        layout.addStretch()

        self.setObjectName("param-label-block")
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


class ParamRow(QWidget):
    def __init__(
        self,
        learner_key: str,
        learner_display_name: str,
        api_param_name: str,
        spec: dict[str, Any],
        param_bindings: dict[str, dict[str, ParamBinding]],
        on_mode_changed_callback=None,
        parent=None,
    ):
        super().__init__(parent)

        default_value = spec["default"]
        manual_values = spec["manual_values"]

        btn_group = QButtonGroup()
        rb_default = QRadioButton("")
        rb_default.setToolTip("Use the typed default value")
        rb_manual = QRadioButton("")
        rb_manual.setToolTip("Use the JSON list from the manual side")
        btn_group.addButton(rb_default, 0)
        btn_group.addButton(rb_manual, 1)

        default_label = QLabel(json_text(default_value))
        default_label.setObjectName("default-value")
        default_label.setToolTip(f"Python value type: {type(default_value).__name__}")

        manual_input = QLineEdit()
        manual_input.setText(json_text(manual_values))
        manual_input.setPlaceholderText("JSON list, e.g. [0.1, 1.0, 10.0]")
        manual_input.setToolTip(
            "Manual mode always expects a JSON list. "
            "For list-valued parameters, use a list of lists, e.g. [[100], [50, 50]]."
        )
        manual_input.setEnabled(False)

        param_block = ParamBlock(api_param_name, spec, field=False)
        field_block = ParamBlock(api_param_name, spec, field=True)

        def on_mode_changed(button_id: int) -> None:
            is_default = button_id == 0
            default_label.setEnabled(is_default)
            manual_input.setEnabled(not is_default)
            if on_mode_changed_callback:
                on_mode_changed_callback()

        btn_group.idClicked.connect(on_mode_changed)
        rb_default.setChecked(True)

        # Connect manual input changes to recalculate combinations
        if on_mode_changed_callback:
            manual_input.textChanged.connect(on_mode_changed_callback)

        # Create lock button with real icon
        lock_button = QPushButton()
        lock_button.setIcon(create_lock_icon(locked=False))
        lock_button.setToolTip("Lock/unlock this parameter from sweeping")
        lock_button.setMaximumWidth(45)
        lock_button.setMaximumHeight(32)
        lock_button.setCheckable(True)
        lock_button.setIconSize(QSize(32, 32))

        def on_lock_toggled(checked: bool) -> None:
            lock_button.setIcon(create_lock_icon(locked=checked))
            # Disable mode/value editing when locked
            rb_default.setEnabled(not checked)
            rb_manual.setEnabled(not checked)
            if not checked:
                # When unlocking, restore proper state based on current mode
                is_manual = btn_group.checkedId() == 1
                manual_input.setEnabled(is_manual)
                default_label.setEnabled(not is_manual)
            else:
                # When locking, disable both
                manual_input.setEnabled(False)
                default_label.setEnabled(False)
            if on_mode_changed_callback:
                on_mode_changed_callback()

        lock_button.clicked.connect(on_lock_toggled)

        # Column 1 - parameter
        param = QHBoxLayout()
        param.setContentsMargins(8, 5, 8, 5)
        param.setSpacing(10)
        param.addWidget(lock_button)
        param.addWidget(param_block)
        param.addStretch()

        col1 = QWidget()
        col1.setLayout(param)
        col1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Column 2 - fields
        field = QHBoxLayout()
        field.setContentsMargins(8, 5, 8, 5)
        field.setSpacing(10)
        field.addWidget(field_block)
        field.addStretch()

        col2 = QWidget()
        col2.setLayout(field)
        col2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Column 3 - default values
        defaults = QHBoxLayout()
        defaults.setContentsMargins(8, 5, 8, 5)
        defaults.setSpacing(10)
        defaults.addWidget(rb_default)
        defaults.addWidget(default_label)
        defaults.addStretch()

        col3 = QWidget()
        col3.setLayout(defaults)
        col3.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Column 4 - manual values
        manuals = QHBoxLayout()
        manuals.setContentsMargins(8, 5, 8, 5)
        manuals.setSpacing(10)
        manuals.addWidget(rb_manual)
        manuals.addWidget(manual_input)
        manuals.addStretch()

        col4 = QWidget()
        col4.setLayout(manuals)
        col4.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Main box
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(col1, 2)
        row.addWidget(vline())
        row.addWidget(col2, 1)
        row.addWidget(vline())
        row.addWidget(col3, 1)
        row.addWidget(vline())
        row.addWidget(col4, 2)

        self.setObjectName("param-row")
        self.setLayout(row)

        # Keep the button group alive. No worker thread owns this object.
        btn_group.setParent(self)

        param_bindings.setdefault(learner_key, {})[api_param_name] = ParamBinding(
            learner_key=learner_key,
            learner_display_name=learner_display_name,
            api_param_name=api_param_name,
            spec=spec,
            manual_input=manual_input,
            btn_group=btn_group,
            default_label=default_label,
            lock_button=lock_button,
        )


class LearnerBlock(QWidget):
    def __init__(
        self,
        learner_key: str,
        learner_spec: dict[str, Any],
        param_bindings: dict[str, dict[str, ParamBinding]],
        on_combinations_changed=None,
        parent=None,
    ):
        super().__init__(parent)
        display_name = learner_spec.get("display_name", learner_key)
        api_class = learner_spec.get("api_class", "")

        outer = QVBoxLayout()
        outer.setContentsMargins(14, 12, 14, 14)
        outer.setSpacing(0)

        # Title with enable checkbox
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)

        title_layout.addStretch()

        enable_checkbox = QCheckBox()
        enable_checkbox.setChecked(True)
        enable_checkbox.setToolTip("Enable/disable this learner")
        enable_checkbox.setObjectName("check-box")
        title_layout.addWidget(enable_checkbox)

        title = QLabel(f"{display_name}")
        title.setObjectName("learner-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        title.setToolTip(f"Python API class: {api_class}")
        title_layout.addWidget(title)
        title_layout.addStretch()

        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        outer.addWidget(title_widget)
        outer.addWidget(hline())
        outer.addSpacing(4)

        header = Header()
        outer.addWidget(header)
        outer.addWidget(hline())

        # Create combinations label early so we can update it
        combinations_label = QLabel("Number of combinations: ")
        combinations_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        def update_combinations() -> None:
            """Recalculate and update the combinations count."""
            try:
                combinations: dict[str, int] = {learner_key: 1}
                for _, param_binding in param_bindings[learner_key].items():
                    combinations[learner_key] *= len(param_binding.selected_values_for_sweep())
                combinations_label.setText(f"# Combinations: {combinations[learner_key]}")
                logger.debug(f"Updated combinations: {combinations[learner_key]}")
                if on_combinations_changed:
                    on_combinations_changed()
            except ValueError as e:
                # Invalid JSON in manual input - show error state
                combinations_label.setText("# Combinations: invalid input")
                logger.warning(f"Invalid manual input: {e}")
                if on_combinations_changed:
                    on_combinations_changed()

        params = learner_spec.get("params", {})
        for i, (api_param_name, param_spec) in enumerate(params.items()):
            outer.addWidget(
                ParamRow(
                    learner_key=learner_key,
                    learner_display_name=display_name,
                    api_param_name=api_param_name,
                    spec=param_spec,
                    param_bindings=param_bindings,
                    on_mode_changed_callback=update_combinations,
                )
            )
            if i < len(params) - 1:
                outer.addWidget(hline())

        # Initial calculation
        update_combinations()
        outer.addWidget(combinations_label)

        self.setObjectName("learner-block")
        self.setLayout(outer)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Store checkbox for later access
        self.enable_checkbox = enable_checkbox
        self.learner_key = learner_key

    def is_enabled(self) -> bool:
        """Check if this learner is enabled."""
        return self.enable_checkbox.isChecked()
