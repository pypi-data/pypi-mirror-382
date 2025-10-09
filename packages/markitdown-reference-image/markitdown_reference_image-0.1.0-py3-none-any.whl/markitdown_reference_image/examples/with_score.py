"""
With score example for markitdown-reference-image package.

This example shows how to add scores to bounding boxes.
"""

from markitdown_reference_image import MarkitdownImageExtractor


def main():
    """With score example."""
    print("🎯 With Score Example")
    print("=" * 50)
    
    # Initialize the extractor
    extractor = MarkitdownImageExtractor()
    
    try:
        # Extract image with highlighted text and score
        image_path = extractor.extract_with_highlight(
            markdown_file="example_document.md",
            chunk_text="important information",
            output_path="highlighted_with_score.png",
            score=0.85  # Score to display in bounding box
        )
        
        print(f"✅ Success! Image with score saved to: {image_path}")
        
    except FileNotFoundError:
        print("❌ Markdown file not found. Please create 'example_document.md' first.")
    except ValueError as e:
        print(f"❌ Text not found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
