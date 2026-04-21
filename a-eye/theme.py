DARK_STYLE = """
QWidget {
    background-color: #1e1e1e;
    color: #e8e8e8;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1e1e1e;
}

QTextEdit, QLineEdit {
    background-color: #2d2d2d;
    color: #e8e8e8;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px;
    selection-background-color: #4A9FFF;
}

QPushButton {
    background-color: #3a3a3a;
    color: #e8e8e8;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px 12px;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #4A9FFF;
}

QPushButton:pressed {
    background-color: #2a2a2a;
}

QComboBox {
    background-color: #2d2d2d;
    color: #e8e8e8;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e8e8e8;
    selection-background-color: #4A9FFF;
    border: 1px solid #444;
}

QSlider::groove:horizontal {
    background: #3a3a3a;
    height: 4px;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #4A9FFF;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: #4A9FFF;
    border-radius: 2px;
}

QTabWidget::pane {
    border: 1px solid #444;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: #2d2d2d;
    color: #aaa;
    padding: 6px 14px;
    border: 1px solid #444;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
}

QTabBar::tab:selected {
    background-color: #1e1e1e;
    color: #e8e8e8;
    border-bottom: 1px solid #1e1e1e;
}

QTabBar::tab:hover {
    color: #e8e8e8;
}

QLabel {
    color: #e8e8e8;
    background: transparent;
}

QScrollBar:vertical {
    background: #2d2d2d;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #555;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QToolButton {
    background-color: #3a3a3a;
    color: #e8e8e8;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px 8px;
}

QToolButton:hover {
    background-color: #4a4a4a;
}

QMessageBox {
    background-color: #1e1e1e;
}
"""
