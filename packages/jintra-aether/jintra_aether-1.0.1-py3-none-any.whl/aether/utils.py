"""
Utility functions for the Aether library.

This module contains helper functions for path sanitization, cycle detection,
logging, and other common operations.
"""

import os
import re
import logging
from typing import Set, List, Any, Dict
from pathlib import Path


# Configure logging
logger = logging.getLogger(__name__)


def sanitize_path(path: str) -> str:
    """
    Sanitize a file path to prevent directory traversal attacks.
    
    Args:
        path: The path to sanitize
        
    Returns:
        Sanitized path
        
    Raises:
        ValueError: If the path contains invalid characters or traversal attempts
    """
    if not path:
        raise ValueError("Path cannot be empty")
    
    # Normalize the path
    normalized = os.path.normpath(path)
    
    # Check for directory traversal attempts
    if ".." in normalized or normalized.startswith("/"):
        raise ValueError(f"Invalid path: {path}")
    
    # Check for invalid characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        if char in normalized:
            raise ValueError(f"Invalid character '{char}' in path: {path}")
    
    return normalized


def detect_cycles(refs: List[str]) -> List[str]:
    """
    Detect circular references in a list of reference paths.
    
    Args:
        refs: List of reference paths to check
        
    Returns:
        List of circular reference paths found
    """
    cycles = []
    visited = set()
    
    for ref in refs:
        if ref in visited:
            cycles.append(ref)
        visited.add(ref)
    
    return cycles


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate that a file has an allowed extension.
    
    Args:
        filename: The filename to check
        allowed_extensions: List of allowed extensions (e.g., ['.png', '.jpg'])
        
    Returns:
        True if the file has an allowed extension, False otherwise
    """
    if not filename:
        return False
    
    _, ext = os.path.splitext(filename.lower())
    return ext in [e.lower() for e in allowed_extensions]


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    return os.path.getsize(file_path)


def is_safe_filename(filename: str) -> bool:
    """
    Check if a filename is safe (no path traversal, no invalid characters).
    
    Args:
        filename: The filename to check
        
    Returns:
        True if the filename is safe, False otherwise
    """
    try:
        sanitize_path(filename)
        return True
    except ValueError:
        return False


def normalize_path(path: str) -> str:
    """
    Normalize a path using forward slashes for consistency.
    
    Args:
        path: The path to normalize
        
    Returns:
        Normalized path
    """
    return path.replace('\\', '/')


def extract_placeholders(text: str, pattern: str = r'\{(.+?)\}') -> List[str]:
    """
    Extract placeholders from text using a regex pattern.
    
    Args:
        text: The text to search for placeholders
        pattern: The regex pattern to use (default: {placeholder})
        
    Returns:
        List of placeholder names found
    """
    return re.findall(pattern, text)


def validate_placeholder_syntax(placeholder: str) -> bool:
    """
    Validate that a placeholder follows the correct syntax.
    
    Args:
        placeholder: The placeholder to validate
        
    Returns:
        True if the placeholder syntax is valid, False otherwise
    """
    # Check for basic placeholder syntax (e.g., "Role.title", "Department.name")
    if not placeholder or not isinstance(placeholder, str):
        return False
    
    # Should contain only alphanumeric characters, dots, and underscores
    return bool(re.match(r'^[a-zA-Z0-9_.]+$', placeholder))


def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a logger with standard configuration.
    
    Args:
        name: The logger name
        level: The logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries, with dict2 taking precedence.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_nested_value(d: Dict[str, Any], key_path: str, sep: str = '.') -> Any:
    """
    Get a value from a nested dictionary using dot notation.
    
    Args:
        d: Dictionary to search
        key_path: Dot-separated path to the value
        sep: Separator for the key path
        
    Returns:
        The value at the specified path, or None if not found
    """
    keys = key_path.split(sep)
    current = d
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def set_nested_value(d: Dict[str, Any], key_path: str, value: Any, sep: str = '.') -> None:
    """
    Set a value in a nested dictionary using dot notation.
    
    Args:
        d: Dictionary to modify
        key_path: Dot-separated path to the value
        value: Value to set
        sep: Separator for the key path
    """
    keys = key_path.split(sep)
    current = d
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
