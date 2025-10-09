"""
Basic extraction example for markitdown-reference-image package.

This example shows the most basic usage pattern.
"""

from markitdown_reference_image import MarkitdownImageExtractor


def main():
    """Basic extraction example."""
    print("🚀 Basic Extraction Example")
    print("=" * 50)
    
    # Initialize the extractor
    extractor = MarkitdownImageExtractor()
    
    # Example markdown file path (you would use your actual file)
    markdown_file = "example_document.md"
    
    # Text chunk to find and highlight
    chunk_text = "important information"
    
    try:
        # Extract image with highlighted text
        image_path = extractor.extract_with_highlight(
            markdown_file=markdown_file,
            chunk_text=chunk_text,
            output_path="highlighted_output.png"
        )
        
        print(f"✅ Success! Image saved to: {image_path}")
        
    except FileNotFoundError:
        print("❌ Markdown file not found. Please create 'example_document.md' first.")
    except ValueError as e:
        print(f"❌ Text not found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
