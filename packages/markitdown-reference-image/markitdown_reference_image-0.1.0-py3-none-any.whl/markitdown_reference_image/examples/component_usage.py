"""
Component usage example for markitdown-reference-image package.

This example shows how to use individual components (TextFinder, ImageProcessor).
"""

import os
import tempfile
from markitdown_reference_image import TextFinder, ImageProcessor
from markitdown_reference_image.text_finder import TextPosition


def main():
    """Component usage example."""
    print("🔧 Component Usage Example")
    print("=" * 50)
    
    # Example markdown content
    markdown_content = """
# Sample Document

This document contains some important information that we want to highlight.

## Section 1

Here is the target text that we want to find and highlight in the image.

## Section 2

More content follows.
"""
    
    # Step 1: Use TextFinder to find text
    print("1. Finding text with TextFinder...")
    finder = TextFinder()
    position = finder.find_text_position(markdown_content, "target text that we want to find")
    
    if position:
        print(f"✅ Text found at line {position.start_line}: '{position.text}'")
        
        # Step 2: Create a simple image for demonstration
        print("2. Creating test image...")
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            img = Image.new('RGB', (400, 300), color='white')
            img.save(f.name)
            test_image_path = f.name
        
        # Step 3: Use ImageProcessor to draw bounding box
        print("3. Drawing bounding box with ImageProcessor...")
        processor = ImageProcessor()
        
        result_path = processor.draw_bounding_box(
            test_image_path,
            position,
            output_path="component_test_output.png",
            score=0.88,
            box_color=(255, 0, 0),      # Red box
            box_width=3,
            score_color=(255, 255, 255), # White text
            score_bg_color=(0, 0, 0)     # Black background
        )
        
        print(f"✅ Component test successful: {result_path}")
        
        # Clean up
        try:
            os.unlink(test_image_path)
        except OSError:
            pass
    else:
        print("❌ Text not found")


if __name__ == "__main__":
    main()
