from PyQt6.QtCore import pyqtSignal, pyqtProperty, Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QFrame
from qfluentwidgets import isDarkTheme
from qfluentwidgets.common.animation import BackgroundAnimationWidget


class CardWidget(BackgroundAnimationWidget, QFrame):
    clicked = pyqtSignal()
    pressed = pyqtSignal()

    def __init__(self, parent=None, type=None):
        QFrame.__init__(self, parent=parent)
        if type:
            BackgroundAnimationWidget.__init__(self, type=type)
        else:
            BackgroundAnimationWidget.__init__(self)
        self._isClickEnabled = False
        self._borderRadius = 4

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.pressed.emit()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()

    def setClickEnabled(self, isEnabled: bool):
        self._isClickEnabled = isEnabled
        self.update()

    def isClickEnabled(self):
        return self._isClickEnabled

    def _normalBackgroundColor(self):
        return QColor(233, 233, 233, 13 if isDarkTheme() else 170)

    def _hoverBackgroundColor(self):
        return QColor(243, 243, 243, 21 if isDarkTheme() else 127)

    def _pressedBackgroundColor(self):
        return QColor(255, 255, 255, 8 if isDarkTheme() else 64)

    def getBorderRadius(self):
        return self._borderRadius

    def setBorderRadius(self, radius: int):
        self._borderRadius = radius
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        r = self.borderRadius

        # draw background
        painter.setPen(Qt.PenStyle.NoPen)
        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setBrush(self.backgroundColor)
        painter.drawRoundedRect(rect, r, r)

    borderRadius = pyqtProperty(int, getBorderRadius, setBorderRadius)
