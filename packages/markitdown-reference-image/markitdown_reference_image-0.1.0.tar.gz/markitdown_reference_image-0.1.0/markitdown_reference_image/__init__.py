"""
Markitdown Reference Image - Extract images from markdown files and highlight text chunks.

This package provides functionality to:
1. Find specific text chunks in markdown files
2. Extract images of the rendered markdown pages
3. Draw bounding boxes around found text chunks
4. Optionally add scores to the bounding boxes
5. Save the processed images

The main API accepts markdown file paths (not content strings) for processing.
"""

from .core import MarkitdownImageExtractor
from .text_finder import TextFinder
from .image_processor import ImageProcessor

__version__ = "0.1.0"
__author__ = "Naveen Kumar Rajarajan"
__email__ = "smazeeapps@gmail.com"

__all__ = [
    "MarkitdownImageExtractor",
    "TextFinder", 
    "ImageProcessor",
]

# Make examples easily accessible
import os
_examples_dir = os.path.join(os.path.dirname(__file__), 'examples')

def get_examples_path():
    """Get the path to the examples directory."""
    return _examples_dir

def list_examples():
    """List available example files."""
    examples = []
    if os.path.exists(_examples_dir):
        for file in os.listdir(_examples_dir):
            if file.endswith('.py') and file != '__init__.py':
                examples.append(file)
    return sorted(examples)
