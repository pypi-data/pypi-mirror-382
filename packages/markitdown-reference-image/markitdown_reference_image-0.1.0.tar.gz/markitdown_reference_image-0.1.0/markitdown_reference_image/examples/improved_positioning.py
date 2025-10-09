#!/usr/bin/env python3
"""
Example demonstrating improved bounding box positioning.

This example shows how the improved positioning algorithm works
with different text chunks and font metrics.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from markitdown_reference_image import MarkitdownImageExtractor


def create_sample_document():
    """Create a sample markdown document for testing."""
    sample_content = """# Sample Document

This is a sample markdown document for testing improved positioning.

## Section 1: Introduction

The markitdown-reference-image package now has improved bounding box positioning.

## Section 2: Features

Here are the key features:

1. **Accurate Positioning**: Better text-to-pixel mapping
2. **Multi-line Support**: Handles text that spans multiple lines
3. **Configurable Metrics**: Customizable font size and spacing
4. **Smart Padding**: Automatic padding around text

## Section 3: Usage

Here is some important information that we want to highlight in the image.

This text contains critical details that should be highlighted with a bounding box.

## Section 4: Conclusion

The improved positioning makes the package much more accurate and useful.
"""
    
    doc_path = "sample_positioning_test.md"
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    return doc_path


def test_improved_positioning():
    """Test the improved positioning with different scenarios."""
    print("🎯 Testing Improved Bounding Box Positioning")
    print("=" * 50)
    
    # Create sample document
    doc_path = create_sample_document()
    
    try:
        # Test 1: Single line text
        print("\n📝 Test 1: Single line text")
        extractor = MarkitdownImageExtractor()
        result1 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="Accurate Positioning",
            output_path="test_single_line.png",
            score=0.95
        )
        print(f"✅ Single line result: {result1}")
        
        # Test 2: Multi-line text
        print("\n📝 Test 2: Multi-line text")
        result2 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="important information that we want to highlight",
            output_path="test_multi_line.png",
            score=0.88
        )
        print(f"✅ Multi-line result: {result2}")
        
        # Test 3: Custom font metrics
        print("\n📝 Test 3: Custom font metrics")
        custom_extractor = MarkitdownImageExtractor(
            font_size=18,  # Larger font
            line_height=28,  # More spacing
            char_width=10   # Wider characters
        )
        result3 = custom_extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="Configurable Metrics",
            output_path="test_custom_metrics.png",
            score=0.92
        )
        print(f"✅ Custom metrics result: {result3}")
        
        # Test 4: Short text
        print("\n📝 Test 4: Short text")
        result4 = extractor.extract_with_highlight(
            markdown_file=doc_path,
            chunk_text="key features",
            output_path="test_short_text.png",
            score=0.85
        )
        print(f"✅ Short text result: {result4}")
        
        print("\n🎉 All positioning tests completed successfully!")
        print("\nGenerated files:")
        print("  - test_single_line.png")
        print("  - test_multi_line.png") 
        print("  - test_custom_metrics.png")
        print("  - test_short_text.png")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    finally:
        # Clean up
        if os.path.exists(doc_path):
            os.unlink(doc_path)
    
    return True


def main():
    """Main function to run the positioning tests."""
    print("🚀 Improved Positioning Example")
    print("This example demonstrates the enhanced bounding box positioning.")
    print("The improvements include:")
    print("  • Better text-to-pixel coordinate mapping")
    print("  • Support for multi-line text spans")
    print("  • Configurable font metrics")
    print("  • Smart padding and minimum size handling")
    print()
    
    success = test_improved_positioning()
    
    if success:
        print("\n✨ Example completed successfully!")
        print("Check the generated PNG files to see the improved positioning.")
    else:
        print("\n❌ Example failed. Check the error messages above.")


if __name__ == "__main__":
    main()
