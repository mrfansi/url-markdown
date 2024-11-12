from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class ActionButtonsWidget(QWidget):
    """Widget containing copy and save action buttons."""

    def __init__(self, on_copy: callable, on_save: callable) -> None:
        super().__init__()
        self.on_copy = on_copy
        self.on_save = on_save
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        self.copy_button = QPushButton("Copy")
        self.save_button = QPushButton("Save")
        
        self.copy_button.setMinimumHeight(40)
        self.save_button.setMinimumHeight(40)
        
        self.copy_button.clicked.connect(self.on_copy)
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setEnabled(False)
        
        layout.addWidget(self.copy_button)
        layout.addWidget(self.save_button)

    def enable_save(self) -> None:
        self.save_button.setEnabled(True)