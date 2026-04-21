import html as _html
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QComboBox, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
import key_store
from providers.ollama import OllamaProvider
from providers.claude import ClaudeProvider
from providers.chatgpt import ChatGPTProvider
from providers.gemini import GeminiProvider
from providers.grok import GrokProvider
from settings_dialog import SettingsDialog


_API_PROVIDER_CLASSES = {
    "Claude": ClaudeProvider,
    "ChatGPT": ChatGPTProvider,
    "Gemini": GeminiProvider,
    "Grok": GrokProvider,
}
_KEY_IDS = {
    "Claude": "claude",
    "ChatGPT": "chatgpt",
    "Gemini": "gemini",
    "Grok": "grok",
}
_OLLAMA_NAME = "Ollama (local)"


class _AIWorker(QThread):
    reply_ready = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, provider, messages, image_b64):
        super().__init__()
        self._provider = provider
        self._messages = messages
        self._image_b64 = image_b64

    def run(self):
        try:
            text = self._provider.send(self._messages, self._image_b64)
            self.reply_ready.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class ChatPanel(QWidget):
    interval_changed = pyqtSignal(int)

    def __init__(self, overlay, capture_thread):
        super().__init__()
        self._overlay = overlay
        self._capture_thread = capture_thread
        self._latest_frame: str | None = None
        self._messages: list[dict] = []
        self._worker: _AIWorker | None = None
        self._provider = None
        self._build_ui()
        capture_thread.frame_ready.connect(self._on_frame)

    def _build_ui(self):
        self.setWindowTitle("A-Eye")
        self.setMinimumWidth(320)
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("AI:"))
        self._provider_combo = QComboBox()
        self._refresh_providers()
        self._provider_combo.currentTextChanged.connect(self._on_provider_changed)
        top.addWidget(self._provider_combo, 1)
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedWidth(32)
        settings_btn.clicked.connect(self._open_settings)
        top.addWidget(settings_btn)
        layout.addLayout(top)

        slider_row = QHBoxLayout()
        slider_row.addWidget(QLabel("Interval:"))
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(1)
        self._slider.setMaximum(10)
        self._slider.setValue(3)
        self._slider.setTickInterval(1)
        self._slider_label = QLabel("3s")
        self._slider.valueChanged.connect(self._on_interval_changed)
        slider_row.addWidget(self._slider, 1)
        slider_row.addWidget(self._slider_label)
        layout.addLayout(slider_row)

        self._history = QTextEdit()
        self._history.setReadOnly(True)
        layout.addWidget(self._history, 1)

        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask the AI something...")
        self._input.returnPressed.connect(self._send)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send)
        input_row.addWidget(self._input, 1)
        input_row.addWidget(send_btn)
        layout.addLayout(input_row)

        self._on_provider_changed(self._provider_combo.currentText())

    def _refresh_providers(self):
        self._provider_combo.blockSignals(True)
        self._provider_combo.clear()

        # Ollama first — no key needed, just check if it's running
        if OllamaProvider().test_connection():
            self._provider_combo.addItem(_OLLAMA_NAME)

        # API-key providers
        for name, key_id in _KEY_IDS.items():
            if key_store.load_key(key_id):
                self._provider_combo.addItem(name)

        if self._provider_combo.count() == 0:
            self._provider_combo.addItem("(None — open ⚙ to set up)")

        self._provider_combo.blockSignals(False)

    def _on_provider_changed(self, name: str):
        if name == _OLLAMA_NAME:
            self._provider = OllamaProvider()
        elif name in _API_PROVIDER_CLASSES:
            key = key_store.load_key(_KEY_IDS[name])
            self._provider = _API_PROVIDER_CLASSES[name](key) if key else None
        else:
            self._provider = None

    def _on_frame(self, b64: str):
        self._latest_frame = b64

    def _on_interval_changed(self, value: int):
        self._slider_label.setText(f"{value}s")
        self._capture_thread.set_interval(value * 1000)
        self.interval_changed.emit(value)

    def _open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            self._refresh_providers()
            self._on_provider_changed(self._provider_combo.currentText())

    def _send(self):
        text = self._input.text().strip()
        if not text or not self._provider:
            return
        self._input.clear()
        self._messages.append({"role": "user", "content": text})
        self._append_bubble("You", text, "#1a3a2a", "#88cc88")

        self._thinking_shown = True
        self._append_bubble("A-Eye", "Thinking...", "#2d2d2d", "#888888")
        self._capture_thread.set_paused(True)
        self._worker = _AIWorker(self._provider, self._messages, self._latest_frame)
        self._worker.reply_ready.connect(self._on_reply)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(lambda: self._capture_thread.set_paused(False))
        self._worker.start()

    def _remove_thinking(self):
        if getattr(self, "_thinking_shown", False):
            cursor = self._history.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            # Remove the entire last block (the Thinking... div)
            doc = self._history.document()
            block = doc.lastBlock()
            cursor.setPosition(block.position())
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            self._thinking_shown = False

    def _on_reply(self, text: str):
        self._messages.append({"role": "assistant", "content": text})
        self._remove_thinking()
        name = self._provider_combo.currentText()
        self._append_bubble(name, text, "#2a3a4a", "#a8d4ff")

    def _on_error(self, msg: str):
        self._remove_thinking()
        self._append_bubble("Error", msg, "#4a1e1e", "#ff9999")

    def _append_bubble(self, sender: str, text: str, bg: str, sender_color: str = "#4A9FFF"):
        safe_text = _html.escape(text).replace("\n", "<br>")
        self._history.append(
            f'<div style="background:{bg};padding:8px;border-radius:6px;margin:4px 0;">'
            f'<b style="color:{sender_color};">{sender}:</b> '
            f'<span style="color:#e8e8e8;">{safe_text}</span>'
            f'</div>'
        )
