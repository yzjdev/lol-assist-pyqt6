from PyQt6.QtCore import QRectF, Qt, QSize
from PyQt6.QtGui import QPainter, QPen, QPixmap, QFont, QPainterPath
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import ProgressRing, isDarkTheme, themeColor, ToolTipFilter, ToolTipPosition


class ProgressArc(ProgressRing):
    def __init__(self, parent=None, useAni=True, text="", fontSize=10):
        self.text = text
        self.fontSize = fontSize
        self.drawVal = 0
        self.ringGap = 30
        super().__init__(parent, useAni=useAni)

    def paintEvent(self, e):
        # 有值取值, 没值保持; self.val 在控件刚实例化时, 前几次update可能会为0
        self.drawVal = self.val or self.drawVal
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cw = self._strokeWidth  # circle thickness
        w = min(self.height(), self.width()) - cw
        rc = QRectF(cw / 2, self.height() / 2 - w / 2, w, w)

        # draw background
        bc = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        pen = QPen(bc, cw, cap=Qt.PenCapStyle.RoundCap, join=Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawArc(rc, (self.ringGap - 90) * 16, (360 - 2 * self.ringGap) * 16)

        if self.maximum() <= self.minimum():
            return

        # draw bar
        pen.setColor(themeColor())
        painter.setPen(pen)
        degree = int(self.drawVal / (self.maximum() -
                                     self.minimum()) * (360 - 2 * self.ringGap))
        painter.drawArc(rc, -(self.ringGap + 90) * 16, -degree * 16)

        painter.setFont(QFont('Microsoft YaHei', self.fontSize, QFont.Weight.Bold))
        text_rect = QRectF(0, self.height() * 0.88,
                           self.width(), self.height() * 0.12)

        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, f"{self.text}")


class AvatarWidget(QWidget):
    def __init__(self,
                 icon=None,  # 'app/resource/images/logo.ico',
                 xpSinceLastLevel=0,
                 xpUntilNextLevel=1,
                 diameter=100,
                 text="1",

                 parent=None):
        super().__init__(parent)
        self.diameter = diameter
        self.sep = .3 * diameter
        self.iconPath = icon

        self.image = QPixmap(self.iconPath)

        self.setFixedSize(self.diameter, self.diameter)

        self.xpSinceLastLevel = xpSinceLastLevel
        self.xpUntilNextLevel = xpUntilNextLevel
        self.progressRing = ProgressArc(
            self, text=text, fontSize=int(.09 * diameter))
        self.progressRing.setTextVisible(False)
        self.progressRing.setFixedSize(self.diameter, self.diameter)

        self.setToolTip(f"Exp: {xpSinceLastLevel} / {xpUntilNextLevel}")
        self.installEventFilter(ToolTipFilter(self, 250, ToolTipPosition.TOP))
        self.paintXpSinceLastLevel = None
        self.paintXpUntilNextLevel = None
        self.callUpdate = False

    def paintEvent(self, event):
        if self.paintXpSinceLastLevel != self.xpSinceLastLevel or self.paintXpUntilNextLevel != self.xpUntilNextLevel or self.callUpdate:
            self.progressRing.setVal(self.xpSinceLastLevel * 100 //
                                     self.xpUntilNextLevel if self.xpSinceLastLevel != 0 else 1)
            self.paintXpUntilNextLevel = self.xpUntilNextLevel
            self.paintXpSinceLastLevel = self.xpSinceLastLevel
            self.callUpdate = False

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        size = (self.size() - QSize(int(self.sep), int(self.sep))) * \
               self.devicePixelRatioF()

        image = self.image

        try:
            # if 'champion' in self.iconPath:
            width = image.width() - 10
            height = image.height() - 10
            image = image.copy(5, 5, width, height)

            scaledImage = image.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                       Qt.TransformationMode.SmoothTransformation)

            clipPath = QPainterPath()

            rect = QRectF(self.sep // 2, self.sep // 2,
                          self.width() - self.sep,
                          self.height() - self.sep)
            clipPath.addEllipse(rect)

            painter.setClipPath(clipPath)
            painter.drawPixmap(rect.toRect(), scaledImage)
        except:
            pass

    def updateIcon(self, icon: str, xpSinceLastLevel=None, xpUntilNextLevel=None, text=""):
        self.iconPath = icon
        self.image = QPixmap(self.iconPath)

        if xpSinceLastLevel is not None and xpUntilNextLevel is not None:
            self.xpSinceLastLevel = xpSinceLastLevel
            self.xpUntilNextLevel = xpUntilNextLevel

            self.setToolTip(f"Exp: {xpSinceLastLevel} / {xpUntilNextLevel}")

        if text:
            self.progressRing.text = text

        self.callUpdate = True
        self.repaint()

    def update_icon(self, icon, xp, level):
        self.updateIcon(icon=icon,
                        xpSinceLastLevel=xp[0],
                        xpUntilNextLevel=xp[1],
                        text=level)
