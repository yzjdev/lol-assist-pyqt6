# coding:utf-8
from typing import Union
import sys

from PyQt6.QtCore import Qt, QSize, QRectF, QEvent
from PyQt6.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect
from qfluentwidgets import FluentIconBase, FluentStyleSheet, isDarkTheme, IndeterminateProgressRing
from qfluentwidgets.common.icon import toQIcon
from qfluentwidgets.components.widgets.flyout import IconWidget

# from ..common.icon import FluentIconBase, drawIcon, toQIcon
# from ..common.style_sheet import isDarkTheme, FluentStyleSheet
# from ..components.widgets import IconWidget
from qframelesswindow import TitleBar


class SplashScreen(QWidget):
    """ Splash screen """

    def __init__(self, parent=None, enableShadow=True):
        super().__init__(parent=parent)
        self.progress_ring = IndeterminateProgressRing(self, Qt.AlignmentFlag.AlignCenter)

        self.shadowEffect = QGraphicsDropShadowEffect(self)

        self.shadowEffect.setColor(QColor(0, 0, 0, 50))
        self.shadowEffect.setBlurRadius(15)
        self.shadowEffect.setOffset(0, 4)

        if enableShadow:
            self.progress_ring.setGraphicsEffect(self.shadowEffect)

        if parent:
            parent.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        if obj is self.parent():
            if e.type() == QEvent.Type.Resize:
                self.resize(e.size())
            elif e.type() == QEvent.Type.ChildAdded:
                self.raise_()

        return super().eventFilter(obj, e)

    def resizeEvent(self, e):
        self.progress_ring.move(self.width() // 2 - self.progress_ring.width() // 2,
                                self.height() // 2 - self.progress_ring.height() // 2)

    def finish(self):
        """ close splash screen """
        self.close()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(Qt.PenStyle.NoPen)

        # draw background
        c = 32 if isDarkTheme() else 255
        painter.setBrush(QColor(c, c, c))
        painter.drawRect(self.rect())
