"""
Pytest configuration and fixtures.
"""

import pytest
import tempfile
import os
from PIL import Image


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """
# Test Document

This is a sample markdown document with some content.

## Section 1

Here is some text that we want to find and highlight.

## Section 2

More content here with **bold text** and `code snippets`.

### Subsection

- List item 1
- List item 2
- List item 3

```python
def hello_world():
    print("Hello, World!")
```
    """


@pytest.fixture
def sample_chunk_text():
    """Sample chunk text to find in markdown."""
    return "text that we want to find"


@pytest.fixture
def test_image():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        # Create a simple 200x200 white image
        img = Image.new('RGB', (200, 200), color='white')
        img.save(f.name)
        yield f.name
        # Clean up
        if os.path.exists(f.name):
            os.unlink(f.name)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
