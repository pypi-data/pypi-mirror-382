"""
Custom styling example for markitdown-reference-image package.

This example shows how to customize the appearance of bounding boxes.
"""

from markitdown_reference_image import MarkitdownImageExtractor


def main():
    """Custom styling example."""
    print("🎨 Custom Styling Example")
    print("=" * 50)
    
    # Initialize the extractor
    extractor = MarkitdownImageExtractor()
    
    try:
        # Extract image with custom styling
        image_path = extractor.extract_with_highlight(
            markdown_file="example_document.md",
            chunk_text="important information",
            output_path="custom_styled_output.png",
            score=0.92,
            box_color=(0, 255, 0),      # Green box
            box_width=5,                # Thicker box
            score_color=(255, 255, 0),  # Yellow text
            score_bg_color=(0, 0, 255)  # Blue background
        )
        
        print(f"✅ Success! Custom styled image saved to: {image_path}")
        
    except FileNotFoundError:
        print("❌ Markdown file not found. Please create 'example_document.md' first.")
    except ValueError as e:
        print(f"❌ Text not found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
