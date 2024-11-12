from typing import Optional, Callable
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

class ActionButtonsWidget(QWidget):
    """
    A widget containing action buttons for markdown operations.
    
    This widget provides Copy and Save buttons with callback functionality
    for clipboard and file operations.
    
    Attributes:
        copy_button (QPushButton): Button for copying content
        save_button (QPushButton): Button for saving content
    """

    def __init__(self, 
                 on_copy: Callable[[], None],
                 on_save: Callable[[], None],
                 parent: Optional[QWidget] = None) -> None:
        """
        Initialize the action buttons widget.
        
        Args:
            on_copy (callable): Callback function for copy action
            on_save (callable): Callback function for save action
            parent (Optional[QWidget]): Parent widget
        """
        super().__init__(parent)
        self._setup_callbacks(on_copy, on_save)
        self._init_ui()

    def _setup_callbacks(self, on_copy: Callable[[], None], on_save: Callable[[], None]) -> None:
        """Setup the callback functions."""
        self.on_copy = on_copy
        self.on_save = on_save

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        
        self._setup_buttons()

    def _setup_buttons(self) -> None:
        """Setup the buttons."""
        self.copy_button = self._create_button("Copy", self.on_copy)
        self.save_button = self._create_button("Save", self.on_save, enabled=False)
        
        self.layout().addWidget(self.copy_button)
        self.layout().addWidget(self.save_button)

    def _create_button(self, text: str, callback: Callable, enabled: bool = True) -> QPushButton:
        """Create a button with the given text, callback, and enabled state."""
        button = QPushButton(text)
        button.setMinimumHeight(40)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        return button

    def enable_save(self) -> None:
        """Enable the save button after content is available."""
        self.save_button.setEnabled(True)