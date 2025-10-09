"""
Command-line interface for markitdown-reference-image.
"""

import argparse
import sys
from pathlib import Path
from .core import MarkitdownImageExtractor
from . import __version__


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Extract images from markdown files and highlight text chunks"
    )
    
    parser.add_argument(
        "markdown_file",
        help="Path to the markdown file"
    )
    
    parser.add_argument(
        "chunk_text",
        help="Text chunk to find and highlight"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output path for the image (default: temporary file)"
    )
    
    parser.add_argument(
        "-s", "--score",
        type=float,
        help="Score to display in the bounding box"
    )
    
    parser.add_argument(
        "--box-color",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="Bounding box color as RGB values (default: 255 0 0)"
    )
    
    parser.add_argument(
        "--box-width",
        type=int,
        help="Bounding box line width (default: 3)"
    )
    
    parser.add_argument(
        "--score-color",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="Score text color as RGB values (default: 255 255 255)"
    )
    
    parser.add_argument(
        "--score-bg-color",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        help="Score background color as RGB values (default: 0 0 0)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"markitdown-reference-image {__version__}"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize extractor
        extractor = MarkitdownImageExtractor()
        
        # Prepare arguments
        kwargs = {}
        if args.box_color:
            kwargs['box_color'] = tuple(args.box_color)
        if args.box_width:
            kwargs['box_width'] = args.box_width
        if args.score_color:
            kwargs['score_color'] = tuple(args.score_color)
        if args.score_bg_color:
            kwargs['score_bg_color'] = tuple(args.score_bg_color)
        
        # Extract image with highlight - FIXED: Use markdown_file instead of markdown_content
        image_path = extractor.extract_with_highlight(
            markdown_file=args.markdown_file,
            chunk_text=args.chunk_text,
            output_path=args.output,
            score=args.score,
            **kwargs
        )
        
        print(f"Image saved to: {image_path}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
