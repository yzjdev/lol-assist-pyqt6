from PyQt6.QtCore import pyqtSignal, Qt, QEvent
from PyQt6.QtGui import QPixmap, QPainterPath, QPainter, QPen, QColor, QMouseEvent
from PyQt6.QtWidgets import QFrame


class RoundIcon(QFrame):
    def __init__(self, icon=None, diameter=26, overscaled=2,
                 borderWidth=2, drawBackground=False, enabled=True, parent=None) -> None:
        super().__init__(parent)
        self.image = QPixmap(icon)

        self.overscaled = overscaled
        self.borderWidth = borderWidth
        self.drawBackground = drawBackground
        self.enabled = enabled

        self.havePic = icon != None

        self.setFixedSize(diameter, diameter)

    def paintEvent(self, event) -> None:
        if not self.havePic:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.image.width() - 2 * self.overscaled
        height = self.image.height() - 2 * self.overscaled

        image = self.image.copy(
            self.overscaled, self.overscaled, width, height)

        size = self.size() * self.devicePixelRatioF()
        image: QPixmap = image.scaled(size,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)

        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())

        painter.setClipPath(path)

        if not self.enabled:
            painter.setOpacity(0.15)

        if self.drawBackground:
            painter.save()
            painter.setBrush(QColor(0, 0, 0))
            painter.drawEllipse(0, 0, self.width(), self.height())
            painter.restore()

        painter.drawPixmap(self.rect(), image)

        if self.borderWidth != 0 and self.enabled:
            painter.save()
            painter.setPen(
                QPen(QColor(120, 90, 40), self.borderWidth, Qt.PenStyle.SolidLine))
            painter.drawEllipse(0, 0, self.width(), self.height())
            painter.restore()

        return super().paintEvent(event)

    def setIcon(self, icon):
        self.havePic = True
        self.image = QPixmap(icon)

        self.repaint()

    def setEnabeld(self, enabled):
        self.enabled = enabled

        self.repaint()


class RoundIconButton(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, champ, diameter=38, overscaled=4, borderWidth=2, parent=None) -> None:
        super().__init__(parent)
        self.champ = champ
        self.image = QPixmap(champ['icon'])

        self.borderWidth = borderWidth
        self.overscaled = overscaled

        self.championName: str = champ['name']
        self.championId = champ['id']

        self.isPressed = False
        self.isHover = False

        self.setFixedSize(diameter, diameter)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        painter.setClipPath(path)

        width = self.image.width() - 2 * self.overscaled
        height = self.image.height() - 2 * self.overscaled

        image = self.image.copy(
            self.overscaled, self.overscaled, width, height)

        size = self.size() * self.devicePixelRatioF()
        image = image.scaled(size,
                             Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)

        if self.isPressed:
            painter.setOpacity(0.63)
        elif self.isHover:
            painter.setOpacity(0.80)
        else:
            painter.setOpacity(1)

        painter.drawPixmap(self.rect(), image)

        painter.setPen(
            QPen(QColor(120, 90, 40), self.borderWidth, Qt.PenStyle.SolidLine))
        painter.drawEllipse(0, 0, self.width(), self.height())

        return super().paintEvent(event)

    def enterEvent(self, a0: QEvent) -> None:
        self.isHover = True
        self.update()
        return super().enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        self.isHover = False
        self.update()
        return super().leaveEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.isPressed = True
        self.update()
        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self.isPressed = False
        self.update()
        ret = super().mouseReleaseEvent(a0)
        self.clicked.emit(self.champ)
        return ret
