from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QCheckBox

from themes.theme import get_theme_tokens


class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._offset = 1.0 if self.isChecked() else 0.0
        self._animation = QPropertyAnimation(self, b"offset", self)
        self._animation.setDuration(110)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 22)
        self.toggled.connect(self._animate_offset)

    def sizeHint(self):
        return self.size()

    def _animate_offset(self, checked: bool) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._offset)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    def get_offset(self) -> float:
        return self._offset

    def set_offset(self, value: float) -> None:
        self._offset = max(0.0, min(1.0, float(value)))
        self.update()

    offset = Property(float, get_offset, set_offset)

    def paintEvent(self, _event) -> None:
        tokens = get_theme_tokens()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = QRectF(1, 1, self.width() - 2, self.height() - 2)
        radius = rect.height() / 2

        if self.isChecked():
            track_color = QColor(tokens["switch_checked"])
            border_color = QColor(tokens["switch_checked"])
        else:
            track_color = QColor(tokens["switch_bg"])
            border_color = QColor(tokens["switch_border"])

        painter.setPen(QPen(border_color, 1))
        painter.setBrush(track_color)
        painter.drawRoundedRect(rect, radius, radius)

        thumb_diameter = rect.height() - 4
        min_x = rect.left() + 2
        max_x = rect.right() - thumb_diameter - 2
        thumb_x = min_x + ((max_x - min_x) * self._offset)
        thumb_rect = QRectF(thumb_x, rect.top() + 2, thumb_diameter, thumb_diameter)

        shadow_rect = thumb_rect.adjusted(0, 0.6, 0, 0.6)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(15, 23, 38, 22))
        painter.drawEllipse(shadow_rect)

        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(thumb_rect)
