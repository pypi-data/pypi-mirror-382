"""
Basic command-line usage example for markitdown-reference-image package.

This example shows basic CLI usage.
"""

import subprocess
import os


def create_sample_document():
    """Create a sample markdown document for testing."""
    sample_content = """# Sample Document

This is a sample markdown document for testing the markitdown-reference-image package.

## Introduction

The package allows you to extract images from markdown files and highlight specific text chunks.

## Features

Here are the key features of the package:

1. **Text Finding**: Find specific text chunks in markdown content
2. **Image Extraction**: Convert markdown to HTML and capture as image
3. **Bounding Boxes**: Draw bounding boxes around found text
4. **Score Display**: Optionally add scores to the bounding boxes

## Example Usage

Here is some important information that we want to highlight in the image.

This text contains critical details that should be highlighted with a bounding box.

## Conclusion

This package makes it easy to create visual references from markdown documents.
"""
    
    with open("sample_document.md", "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print("✅ Created sample_document.md")


def main():
    """Basic CLI example."""
    print("💻 Command Line - Basic Usage")
    print("=" * 50)
    
    # Create sample document if it doesn't exist
    if not os.path.exists("sample_document.md"):
        create_sample_document()
    
    # Basic command
    cmd = [
        "markitdown-extract",
        "sample_document.md",
        "important information that we want to highlight",
        "-o", "cli_basic_output.png"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Success: {result.stdout.strip()}")
        else:
            print(f"❌ Error: {result.stderr.strip()}")
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
    except FileNotFoundError:
        print("❌ Command not found. Make sure the package is installed with console scripts.")
        print("   Install with: pip install -e .")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
