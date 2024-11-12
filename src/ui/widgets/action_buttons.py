from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton  # Removed QStyle
from PySide6.QtCore import Qt  # Removed QIcon import

class ActionButtonsWidget(QWidget):
    """
    A widget containing action buttons for markdown operations.
    
    This widget provides Copy and Save buttons with callback functionality
    for clipboard and file operations.
    
    Attributes:
        copy_button (QPushButton): Button for copying content
        save_button (QPushButton): Button for saving content
    """

    def __init__(self, on_copy: callable, on_save: callable) -> None:
        """
        Initialize the action buttons widget.
        
        Args:
            on_copy (callable): Callback function for copy action
            on_save (callable): Callback function for save action
        """
        super().__init__()
        self.on_copy = on_copy
        self.on_save = on_save
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
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
        """Enable the save button after content is available."""
        self.save_button.setEnabled(True)