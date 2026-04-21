import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPoint
import key_store
from overlay import OverlayWindow
from capture import CaptureThread
from chat_panel import ChatPanel
from settings_dialog import SettingsDialog


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("A-Eye")

    overlay = OverlayWindow()
    capture = CaptureThread(overlay, interval_ms=3000)

    chat = ChatPanel(overlay, capture)

    # Position chat panel to the right of the overlay
    overlay.move(200, 200)
    overlay_right = overlay.x() + overlay.width() + 12
    chat.move(QPoint(overlay_right, overlay.y()))

    overlay.show()
    chat.show()

    # Open settings on first run if no keys are saved
    if not any(key_store.load_key(p) for p in ["claude", "chatgpt", "gemini", "grok"]):
        dlg = SettingsDialog()
        dlg.exec()
        chat._refresh_providers()
        chat._on_provider_changed(chat._provider_combo.currentText())

    capture.start()

    code = app.exec()
    capture.stop()
    sys.exit(code)


if __name__ == "__main__":
    main()
