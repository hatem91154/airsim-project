from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt


class BaseDisplay(QWidget):
    """
    Base class for all display widgets in PyQt Live Tuner.
    
    This provides common functionality for all display widgets:
    - Consistent styling and layout
    - Title and border
    - Optional controls area
    - Resize handling
    
    All display widgets should inherit from this class.
    
    Config options:
    - title (str): Title for the display widget
    - with_controls (bool): Whether to include a control area
    - size (tuple): Default size as (width, height)
    - show_title (bool): Whether to show the title
    """
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the base display widget.
        
        Args:
            parent: Parent widget (default: None)
            config: Configuration dictionary with options (default: None)
                   See class docstring for available options
        """
        super().__init__(parent)
        
        # Default configuration
        self.default_config = {
            "title": "Display Widget",
            "with_controls": False,  # No controls by default
            "size": (400, 300),
            "show_title": True
        }
        
        # Update with provided config
        self.config = self.default_config.copy()
        if config is not None:
            self.config.update(config)
        
        # Set properties from config
        self.title = self.config["title"]
        self.with_controls = self.config["with_controls"]
        self.default_size = self.config["size"]
        self.show_title = self.config["show_title"]
        
        # Initialize UI
        self._init_base_ui()
    
    def _init_base_ui(self):
        """Initialize the base UI components shared by all display widgets"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        
        # Add title if needed
        if self.show_title:
            self.title_label = QLabel(self.title)
            self.title_label.setAlignment(Qt.AlignCenter)
            self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.main_layout.addWidget(self.title_label)
        
        # Content area - will be filled by derived classes
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.setMinimumSize(self.default_size[0], self.default_size[1])
        self.content_widget.setStyleSheet("border: 1px solid #cccccc; background-color: #f0f0f0;")
        
        self.main_layout.addWidget(self.content_widget, 1)  # 1 = stretch factor
        
        # Controls area if needed
        if self.with_controls:
            self.control_widget = QWidget()
            self.control_layout = QHBoxLayout(self.control_widget)
            self.control_layout.setContentsMargins(0, 4, 0, 0)
            self.main_layout.addWidget(self.control_widget)
        
        self.setLayout(self.main_layout)
    
    def add_control(self, widget):
        """
        Add a control widget to the controls area.
        
        Args:
            widget: The QWidget to add to the controls area
            
        Raises:
            RuntimeError: If the display was initialized with with_controls=False
        """
        if not self.with_controls:
            raise RuntimeError("Cannot add controls when with_controls is False")
        
        self.control_layout.addWidget(widget)
    
    def clear(self):
        """
        Clear the display content.
        
        This method should be implemented by derived classes.
        """
        pass
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        # Derived classes should override this if needed
        
    def save_state(self):
        """
        Save the current state of the display.
        
        Returns:
            dict: A dictionary containing the state of the display
        """
        return {
            "title": self.title,
            "size": (self.width(), self.height())
        }
    
    def load_state(self, state):
        """
        Load a previously saved state.
        
        Args:
            state: A dictionary containing the state to load
        """
        if "title" in state:
            self.title = state["title"]
            if self.show_title and hasattr(self, "title_label"):
                self.title_label.setText(self.title)
        
        if "size" in state:
            self.resize(*state["size"])