"""File handling utilities for PyQt Live Tuner.

This module provides the FileHandler class for managing configuration files,
including loading and saving parameter values to JSON.
"""

import json
import os
from typing import Dict, Any, Optional

from .logger import logger


class FileHandler:
    """Handler for file operations related to parameter configurations.
    
    This class is responsible for loading and saving parameter configurations to JSON files.
    It abstracts the file I/O operations from the main application class.
    
    Attributes:
        _last_save_path (str): Path of the last saved configuration file
    """
    
    def __init__(self):
        """Initialize the file handler."""
        self._last_save_path = None
        
    def save_config(self, values: Dict[str, Any], file_path: Optional[str] = None) -> Optional[str]:
        """Save parameter values to a JSON configuration file.
        
        Args:
            values: Parameter values to save
            file_path: Path to save to (if None, uses last saved path)
            
        Returns:
            Path of the saved file, or None if save was canceled or failed
        """
        path = file_path or self._last_save_path
        if not path:
            return None
            
        try:
            with open(path, "w") as f:
                json.dump(values, f, indent=2)
            self._last_save_path = path
            return path
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return None
            
    def load_config(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load parameter values from a JSON configuration file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Dictionary of loaded values, or None if load failed
        """
        if not file_path or not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return None
            
    def get_save_path(self) -> str:
        """Get the path of the last saved file.
        
        Returns:
            Path of the last saved file, or None if no file has been saved
        """
        return self._last_save_path
        
    def set_save_path(self, path: str) -> None:
        """Set the path for future save operations.
        
        Args:
            path: New save path to use
        """
        self._last_save_path = path