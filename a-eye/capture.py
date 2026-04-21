import base64
import io
from PyQt6.QtCore import QThread, pyqtSignal
import mss
from PIL import Image


class CaptureThread(QThread):
    frame_ready = pyqtSignal(str)  # emits base64-encoded PNG

    def __init__(self, overlay, interval_ms: int = 3000):
        super().__init__()
        self._overlay = overlay
        self._interval_ms = interval_ms
        self._paused = False
        self._running = True

    def set_interval(self, ms: int):
        self._interval_ms = ms

    def set_paused(self, paused: bool):
        self._paused = paused

    def stop(self):
        self._running = False
        self.wait()

    def run(self):
        with mss.mss() as sct:
            while self._running:
                if not self._paused:
                    x, y, w, h = self._overlay.get_region()
                    if w > 0 and h > 0:
                        monitor = {"left": x, "top": y, "width": w, "height": h}
                        shot = sct.grab(monitor)
                        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        b64 = base64.b64encode(buf.getvalue()).decode()
                        self.frame_ready.emit(b64)
                self.msleep(self._interval_ms)
