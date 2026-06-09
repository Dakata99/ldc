from __future__ import annotations

import sys

from AnyQt.QtWidgets import QApplication

from liver.tuner.window import MainWindow
from liver.tuner.styles import STYLESHEET


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.showMaximized()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
