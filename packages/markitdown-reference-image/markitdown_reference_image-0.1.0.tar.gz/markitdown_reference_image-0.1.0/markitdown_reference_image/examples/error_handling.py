"""
Error handling example for markitdown-reference-image package.

This example shows proper error handling patterns.
"""

from markitdown_reference_image import MarkitdownImageExtractor


def main():
    """Error handling example."""
    print("⚠️ Error Handling Example")
    print("=" * 50)
    
    # Initialize the extractor
    extractor = MarkitdownImageExtractor()
    
    # Test cases with different error scenarios
    test_cases = [
        {
            "name": "Valid file and text",
            "file": "example_document.md",
            "text": "important information",
            "should_succeed": True
        },
        {
            "name": "File not found",
            "file": "nonexistent.md",
            "text": "some text",
            "should_succeed": False
        },
        {
            "name": "Text not found",
            "file": "example_document.md",
            "text": "nonexistent text",
            "should_succeed": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        
        try:
            image_path = extractor.extract_with_highlight(
                markdown_file=test_case["file"],
                chunk_text=test_case["text"],
                output_path=f"test_{test_case['name'].replace(' ', '_')}.png"
            )
            
            if test_case["should_succeed"]:
                print(f"✅ Expected success: {image_path}")
            else:
                print(f"❌ Unexpected success: {image_path}")
                
        except FileNotFoundError as e:
            if not test_case["should_succeed"] and "nonexistent" in test_case["file"]:
                print(f"✅ Expected FileNotFoundError: {e}")
            else:
                print(f"❌ Unexpected FileNotFoundError: {e}")
                
        except ValueError as e:
            if not test_case["should_succeed"] and "nonexistent" in test_case["text"]:
                print(f"✅ Expected ValueError: {e}")
            else:
                print(f"❌ Unexpected ValueError: {e}")
                
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
