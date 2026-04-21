from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QMessageBox, QToolButton
)
from PyQt6.QtCore import Qt
import key_store
from providers.ollama import OllamaProvider
from providers.claude import ClaudeProvider
from providers.chatgpt import ChatGPTProvider
from providers.gemini import GeminiProvider
from providers.grok import GrokProvider


_INSTRUCTIONS = {
    "claude": (
        "How to get your Claude API key:\n\n"
        "1. Go to console.anthropic.com and sign in (or create an account)\n"
        "2. Click your profile icon in the top-right → 'API Keys'\n"
        "3. Click 'Create Key', give it a name, then copy it\n\n"
        "Note: Requires a paid Anthropic account."
    ),
    "chatgpt": (
        "How to get your ChatGPT API key:\n\n"
        "1. Go to platform.openai.com and sign in (or create an account)\n"
        "2. Click the lock icon in the left menu → 'API Keys'\n"
        "3. Click 'Create new secret key' and copy it immediately\n"
        "   (it is only shown once!)\n\n"
        "Note: Requires a paid OpenAI account with billing set up."
    ),
    "gemini": (
        "How to get your Gemini API key:\n\n"
        "1. Go to aistudio.google.com and sign in with your Google account\n"
        "2. Click 'Get API Key' in the top-left corner\n"
        "3. Click 'Create API Key in new project', then copy it\n\n"
        "Note: Gemini offers a free tier."
    ),
    "grok": (
        "How to get your Grok API key:\n\n"
        "1. Go to console.x.ai and sign in with your X (Twitter) account\n"
        "2. Click 'API Keys' in the left menu\n"
        "3. Click 'Create API Key', give it a name, then copy it\n\n"
        "Note: Requires an xAI account with billing set up."
    ),
}

_PROVIDER_CLASSES = {
    "claude": ClaudeProvider,
    "chatgpt": ChatGPTProvider,
    "gemini": GeminiProvider,
    "grok": GrokProvider,
}

_DISPLAY_NAMES = {
    "claude": "Claude (Anthropic)",
    "chatgpt": "ChatGPT (OpenAI)",
    "gemini": "Gemini (Google)",
    "grok": "Grok (xAI)",
}

_OLLAMA_INSTRUCTIONS = (
    "Ollama runs an AI model locally on your PC — no account or internet needed.\n\n"
    "Setup (one-time):\n"
    "  1. Download and install Ollama from ollama.com\n"
    "  2. Open Command Prompt and run:\n"
    "         ollama pull llava\n"
    "  3. Wait for the download to finish (~4 GB)\n"
    "  4. Click 'Check Again' below — status should turn green\n\n"
    "Minimum requirements: 8 GB RAM, modern CPU (GPU optional but faster)"
)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, focus_ollama: bool = False):
        super().__init__(parent)
        self.setWindowTitle("A-Eye Settings")
        self.setMinimumWidth(500)
        self._fields: dict[str, QLineEdit] = {}
        self._ollama_status_label: QLabel | None = None
        self._tabs: QTabWidget | None = None
        self._build_ui()
        self._load_saved_keys()
        self._refresh_ollama_status()
        if focus_ollama and self._tabs:
            self._tabs.setCurrentIndex(0)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self._tabs = QTabWidget()

        # --- Ollama tab (first) ---
        ollama_tab = QWidget()
        ot_layout = QVBoxLayout(ollama_tab)
        ot_layout.setSpacing(10)
        ot_layout.addWidget(QLabel("<b>Ollama — Free Local AI (Recommended)</b>"))

        status_row = QHBoxLayout()
        self._ollama_status_label = QLabel("Checking...")
        check_btn = QPushButton("Check Again")
        check_btn.setFixedWidth(100)
        check_btn.clicked.connect(self._refresh_ollama_status)
        status_row.addWidget(QLabel("Status:"))
        status_row.addWidget(self._ollama_status_label)
        status_row.addStretch()
        status_row.addWidget(check_btn)
        ot_layout.addLayout(status_row)

        instructions = QLabel(_OLLAMA_INSTRUCTIONS)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background:#f5f5f5; padding:10px; border-radius:4px;")
        ot_layout.addWidget(instructions)
        ot_layout.addStretch()
        self._tabs.addTab(ollama_tab, "Ollama (Free)")

        # --- API key tabs ---
        for provider_id, display_name in _DISPLAY_NAMES.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setSpacing(8)
            tab_layout.addWidget(QLabel(f"<b>{display_name}</b>"))

            key_row = QHBoxLayout()
            field = QLineEdit()
            field.setEchoMode(QLineEdit.EchoMode.Password)
            field.setPlaceholderText("Paste your API key here...")
            self._fields[provider_id] = field

            toggle_btn = QToolButton()
            toggle_btn.setText("Show")
            toggle_btn.setCheckable(True)
            toggle_btn.toggled.connect(lambda checked, f=field, b=toggle_btn: (
                f.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password),
                b.setText("Hide" if checked else "Show")
            ))

            test_btn = QPushButton("Test")
            test_btn.setFixedWidth(60)
            test_btn.clicked.connect(lambda _, pid=provider_id: self._test_key(pid))

            key_row.addWidget(field)
            key_row.addWidget(toggle_btn)
            key_row.addWidget(test_btn)
            tab_layout.addLayout(key_row)

            help_label = QLabel('<a href="#">How to get this key ▼</a>')
            help_label.setTextFormat(Qt.TextFormat.RichText)
            instructions_label = QLabel(_INSTRUCTIONS[provider_id])
            instructions_label.setWordWrap(True)
            instructions_label.setStyleSheet("background:#f5f5f5; padding:8px; border-radius:4px;")
            instructions_label.setVisible(False)

            help_label.linkActivated.connect(
                lambda _, lbl=instructions_label, hl=help_label: (
                    lbl.setVisible(not lbl.isVisible()),
                    hl.setText('How to get this key ▲' if lbl.isVisible() else 'How to get this key ▼')
                )
            )

            tab_layout.addWidget(help_label)
            tab_layout.addWidget(instructions_label)
            tab_layout.addStretch()
            self._tabs.addTab(tab, display_name.split(" ")[0])

        layout.addWidget(self._tabs)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

    def _refresh_ollama_status(self):
        ok = OllamaProvider().test_connection()
        if ok:
            self._ollama_status_label.setText("✓ Running — llava model ready")
            self._ollama_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self._ollama_status_label.setText("✗ Not detected")
            self._ollama_status_label.setStyleSheet("color: red; font-weight: bold;")

    def _load_saved_keys(self):
        for provider_id, field in self._fields.items():
            field.setText(key_store.load_key(provider_id))

    def _test_key(self, provider_id: str):
        key = self._fields[provider_id].text().strip()
        if not key:
            QMessageBox.warning(self, "No Key", "Please enter an API key first.")
            return
        cls = _PROVIDER_CLASSES[provider_id]
        try:
            ok = cls(key).test_connection()
        except Exception:
            ok = False
        if ok:
            QMessageBox.information(self, "Connected", f"{_DISPLAY_NAMES[provider_id]}: connected successfully!")
        else:
            QMessageBox.critical(self, "Failed", "Could not connect. Check your API key and try again.")

    def _save(self):
        for provider_id, field in self._fields.items():
            key_store.save_key(provider_id, field.text().strip())
        self.accept()
