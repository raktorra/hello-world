from PyQt6.QtWidgets import QWidget, QSizeGrip, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor


BORDER = 4
HANDLE = 16


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMinimumSize(100, 100)
        self.resize(400, 300)
        self._drag_pos = None

        # Size grip in bottom-right corner
        self._grip = QSizeGrip(self)
        self._grip.setFixedSize(HANDLE, HANDLE)

    def resizeEvent(self, event):
        self._grip.move(self.width() - HANDLE, self.height() - HANDLE)

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor("#4A9FFF"), BORDER)
        painter.setPen(pen)
        painter.drawRect(
            BORDER // 2, BORDER // 2,
            self.width() - BORDER, self.height() - BORDER
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def get_region(self) -> tuple[int, int, int, int]:
        pos = self.mapToGlobal(QPoint(BORDER, BORDER))
        screen = QApplication.primaryScreen()
        ratio = screen.devicePixelRatio()
        x = int(pos.x() * ratio)
        y = int(pos.y() * ratio)
        w = int((self.width() - BORDER * 2) * ratio)
        h = int((self.height() - BORDER * 2) * ratio)
        return x, y, w, h
