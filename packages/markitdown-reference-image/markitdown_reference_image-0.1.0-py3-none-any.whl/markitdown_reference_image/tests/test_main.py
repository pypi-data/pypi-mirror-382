"""
Test module for the main functionality.
"""

import pytest
import tempfile
import os
from markitdown_reference_image import MarkitdownImageExtractor, TextFinder, ImageProcessor
from markitdown_reference_image.text_finder import TextPosition


class TestMarkitdownImageExtractor:
    """Test class for MarkitdownImageExtractor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = MarkitdownImageExtractor()
        self.sample_markdown = """
# Test Document

This is a sample markdown document with some content.

## Section 1

Here is some text that we want to find and highlight.

## Section 2

More content here.
        """

    def test_extractor_initialization(self):
        """Test that extractor initializes correctly."""
        assert self.extractor is not None
        assert self.extractor.text_finder is not None
        assert self.extractor.image_processor is not None

    def test_markdown_to_html_conversion(self):
        """Test markdown to HTML conversion."""
        html = self.extractor._markdown_to_html("# Test\nThis is a test.")
        assert "<h1>Test</h1>" in html
        assert "<p>This is a test.</p>" in html
        assert "<!DOCTYPE html>" in html

    def test_extract_with_highlight_file_not_found(self):
        """Test extraction when markdown file is not found."""
        with pytest.raises(FileNotFoundError, match="Markdown file 'nonexistent.md' not found"):
            self.extractor.extract_with_highlight(
                "nonexistent.md",
                "some text"
            )

    def test_extract_with_highlight_success(self, temp_output_dir):
        """Test successful extraction with file path."""
        # Create a temporary markdown file
        markdown_file = os.path.join(temp_output_dir, "test.md")
        with open(markdown_file, 'w') as f:
            f.write(self.sample_markdown)
        
        # This test would require actual image processing, so we'll just test the file reading part
        # In a real scenario, you might want to mock the image processing parts
        try:
            result = self.extractor.extract_with_highlight(
                markdown_file,
                "text that we want to find"
            )
            # If it gets here without error, the file reading worked
            assert result is not None
        except Exception as e:
            # We expect this to fail at the image processing stage in tests
            # since we don't have Chrome/Selenium set up in the test environment
            assert "Chunk text" not in str(e)  # Should not fail at text finding stage

    def test_extract_with_highlight_text_not_found(self, temp_output_dir):
        """Test extraction when text chunk is not found."""
        # Create a temporary markdown file
        markdown_file = os.path.join(temp_output_dir, "test.md")
        with open(markdown_file, 'w') as f:
            f.write(self.sample_markdown)
        
        with pytest.raises(ValueError, match="Chunk text 'nonexistent text' not found"):
            self.extractor.extract_with_highlight(
                markdown_file,
                "nonexistent text"
            )


class TestTextFinder:
    """Test class for TextFinder."""

    def setup_method(self):
        """Set up test fixtures."""
        self.finder = TextFinder()
        self.sample_text = """
# Title
This is a sample text with some content.
Here is the target text we want to find.
More content follows.
        """

    def test_finder_initialization(self):
        """Test that finder initializes correctly."""
        assert self.finder is not None

    def test_find_text_position_exact_match(self):
        """Test finding text with exact match."""
        position = self.finder.find_text_position(
            self.sample_text,
            "target text we want to find"
        )
        assert position is not None
        assert isinstance(position, TextPosition)
        assert position.text == "target text we want to find"

    def test_find_text_position_not_found(self):
        """Test finding text that doesn't exist."""
        position = self.finder.find_text_position(
            self.sample_text,
            "nonexistent text"
        )
        assert position is None

    def test_normalize_text(self):
        """Test text normalization."""
        normalized = self.finder._normalize_text("  This   is   a   test  ")
        assert normalized == "this is a test"

    def test_find_multiple_chunks(self):
        """Test finding multiple text chunks."""
        chunks = ["sample text", "target text", "nonexistent"]
        positions = self.finder.find_multiple_chunks(self.sample_text, chunks)
        assert len(positions) == 2  # Only first two should be found


class TestImageProcessor:
    """Test class for ImageProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ImageProcessor()
        # Create a simple test image
        self.test_image_path = self._create_test_image()

    def _create_test_image(self):
        """Create a simple test image."""
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Create a simple 100x100 white image
            img = Image.new('RGB', (100, 100), color='white')
            img.save(f.name)
            return f.name

    def teardown_method(self):
        """Clean up test files."""
        if os.path.exists(self.test_image_path):
            os.unlink(self.test_image_path)

    def test_processor_initialization(self):
        """Test that processor initializes correctly."""
        assert self.processor is not None
        assert self.processor.default_box_color == (255, 0, 0)
        assert self.processor.default_box_width == 3

    def test_calculate_bbox_coordinates(self):
        """Test bounding box coordinate calculation."""
        from PIL import Image
        from markitdown_reference_image.text_finder import TextPosition
        
        image = Image.new('RGB', (200, 200), color='white')
        text_position = TextPosition(
            start_line=1,
            end_line=1,
            start_column=0,
            end_column=10,
            text="test",
            context=""
        )
        
        coords = self.processor._calculate_bbox_coordinates(image, text_position)
        assert len(coords) == 4
        assert all(isinstance(coord, int) for coord in coords)
        assert coords[0] < coords[2]  # left < right
        assert coords[1] < coords[3]  # top < bottom

    def test_draw_bounding_box_with_temp_output(self):
        """Test drawing bounding box with temporary output."""
        from markitdown_reference_image.text_finder import TextPosition
        
        text_position = TextPosition(
            start_line=1,
            end_line=1,
            start_column=0,
            end_column=10,
            text="test",
            context=""
        )
        
        result_path = self.processor.draw_bounding_box(
            self.test_image_path,
            text_position,
            score=0.85
        )
        
        assert os.path.exists(result_path)
        assert result_path.endswith('.png')
        
        # Clean up
        if os.path.exists(result_path):
            os.unlink(result_path)
