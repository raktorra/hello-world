import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPoint
import key_store
from providers.ollama import OllamaProvider
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

    overlay.move(200, 200)
    chat.move(QPoint(overlay.x() + overlay.width() + 12, overlay.y()))

    overlay.show()
    chat.show()

    ollama_ready = OllamaProvider().test_connection()
    has_api_key = any(key_store.load_key(p) for p in ["claude", "chatgpt", "gemini", "grok"])

    if not ollama_ready and not has_api_key:
        dlg = SettingsDialog(focus_ollama=True)
        dlg.exec()
        chat._refresh_providers()
        chat._on_provider_changed(chat._provider_combo.currentText())

    capture.start()

    code = app.exec()
    capture.stop()
    sys.exit(code)


if __name__ == "__main__":
    main()
