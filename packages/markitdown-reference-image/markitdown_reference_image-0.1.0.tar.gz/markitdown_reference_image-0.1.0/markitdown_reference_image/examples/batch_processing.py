"""
Batch processing example for markitdown-reference-image package.

This example shows how to process multiple markdown files.
"""

import os
from pathlib import Path
from markitdown_reference_image import MarkitdownImageExtractor


def main():
    """Batch processing example."""
    print("📚 Batch Processing Example")
    print("=" * 50)
    
    # Initialize the extractor
    extractor = MarkitdownImageExtractor()
    
    # List of markdown files to process
    markdown_files = [
        "document1.md",
        "document2.md", 
        "document3.md"
    ]
    
    # Text chunks to find in each file
    chunk_texts = [
        "key information",
        "important data",
        "critical details"
    ]
    
    # Create output directory
    output_dir = Path("batch_output")
    output_dir.mkdir(exist_ok=True)
    
    results = []
    
    for i, (md_file, chunk_text) in enumerate(zip(markdown_files, chunk_texts)):
        try:
            output_path = output_dir / f"highlighted_{i+1}.png"
            
            image_path = extractor.extract_with_highlight(
                markdown_file=md_file,
                chunk_text=chunk_text,
                output_path=str(output_path),
                score=0.8 + (i * 0.05)  # Varying scores
            )
            
            results.append((md_file, "✅ Success", image_path))
            print(f"✅ Processed {md_file} -> {image_path}")
            
        except FileNotFoundError:
            results.append((md_file, "❌ File not found", None))
            print(f"❌ File not found: {md_file}")
        except ValueError as e:
            results.append((md_file, f"❌ Text not found: {e}", None))
            print(f"❌ Text not found in {md_file}: {e}")
        except Exception as e:
            results.append((md_file, f"❌ Error: {e}", None))
            print(f"❌ Error processing {md_file}: {e}")
    
    print(f"\n📊 Batch processing complete: {len([r for r in results if 'Success' in r[1]])}/{len(results)} successful")


if __name__ == "__main__":
    main()
