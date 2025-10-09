# Markitdown Reference Image

A Python package for extracting images from markdown files and highlighting specific text chunks with bounding boxes.

## Features

- Find specific text chunks in markdown content
- Convert markdown to HTML and capture as image
- Draw bounding boxes around found text chunks
- Optionally add scores to the bounding boxes
- Save processed images to specified paths or temporary files

## Installation

```bash
pip install markitdown-reference-image
```

## Usage

### Basic Usage

```python
from markitdown_reference_image import MarkitdownImageExtractor

# Initialize the extractor
extractor = MarkitdownImageExtractor()

# Path to your markdown file
markdown_file = "document.md"

# Text chunk to find and highlight
chunk_text = "target text that we want to find"

# Extract image with highlighted text
image_path = extractor.extract_with_highlight(
    markdown_file=markdown_file,
    chunk_text=chunk_text,
    output_path="highlighted_image.png"
)

print(f"Image saved to: {image_path}")
```

### With Score

```python
# Extract image with highlighted text and score
image_path = extractor.extract_with_highlight(
    markdown_file="document.md",
    chunk_text=chunk_text,
    output_path="highlighted_image_with_score.png",
    score=0.85  # Score to display in the bounding box
)
```

### Using Temporary Output

```python
# If no output_path is provided, a temporary file will be created
image_path = extractor.extract_with_highlight(
    markdown_file="document.md",
    chunk_text=chunk_text
    # No output_path specified - will use temporary file
)
```

### Custom Styling

```python
# Customize the bounding box appearance
image_path = extractor.extract_with_highlight(
    markdown_file="document.md",
    chunk_text=chunk_text,
    output_path="custom_highlighted_image.png",
    score=0.92,
    box_color=(0, 255, 0),  # Green box
    box_width=5,            # Thicker box
    score_color=(255, 255, 0),  # Yellow text
    score_bg_color=(0, 0, 255)  # Blue background
)
```

### Improved Positioning

```python
# Use custom font metrics for better positioning
extractor = MarkitdownImageExtractor(
    font_size=18,    # Larger font size
    line_height=28,  # More line spacing
    char_width=10    # Wider character width
)

image_path = extractor.extract_with_highlight(
    markdown_file="document.md",
    chunk_text=chunk_text,
    output_path="improved_positioning.png",
    score=0.95
)
```

## Examples

The package includes comprehensive examples in the `markitdown_reference_image/examples/` directory:

### Quick Example Runner
```bash
python run_examples.py
```

### Individual Examples
```bash
# Basic usage examples
python -m markitdown_reference_image.examples.basic_extraction
python -m markitdown_reference_image.examples.with_score
python -m markitdown_reference_image.examples.custom_styling

# Advanced usage examples  
python -m markitdown_reference_image.examples.batch_processing
python -m markitdown_reference_image.examples.component_usage
python -m markitdown_reference_image.examples.error_handling

# Command-line examples
python -m markitdown_reference_image.examples.cli_basic
python -m markitdown_reference_image.examples.cli_with_score
python -m markitdown_reference_image.examples.cli_custom_styling
```

### Available Examples:

**Basic Usage:**
- **`basic_extraction.py`** - Basic image extraction
- **`with_score.py`** - Adding scores to bounding boxes
- **`custom_styling.py`** - Custom styling options

**Advanced Usage:**
- **`batch_processing.py`** - Batch processing multiple files
- **`component_usage.py`** - Using individual components
- **`error_handling.py`** - Proper error handling

**Command Line:**
- **`cli_basic.py`** - Basic CLI usage
- **`cli_with_score.py`** - CLI with score display
- **`cli_custom_styling.py`** - CLI with custom styling

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/markitdown-reference-image.git
cd markitdown-reference-image
```

2. Install in development mode:
```bash
pip install -e .
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8 .
mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite
6. Submit a pull request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.
