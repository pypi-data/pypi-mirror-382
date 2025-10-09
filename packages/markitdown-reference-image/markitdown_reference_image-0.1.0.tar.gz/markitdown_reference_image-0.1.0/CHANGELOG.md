# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **DOM-based positioning**: Bounding boxes now use actual pixel coordinates from browser rendering
- **JavaScript-based text finding**: Uses `window.find()` API for multi-line text support
- New `draw_bounding_box_from_coords()` method for direct coordinate-based drawing
- Multi-line text highlighting example (`multiline_text_example.py`)
- Coordinate validation to prevent invalid bounding boxes
- Retry logic with multiple attempts to find highlighted elements
- Added padding around bounding boxes for better visual appearance
- Comprehensive positioning improvements documentation (POSITIONING_IMPROVEMENTS.md)
- Enhanced error handling with fallback coordinates

### Changed
- **BREAKING**: Bounding box positioning now uses actual DOM coordinates instead of character-based calculation
- **Text finding now uses JavaScript `window.find()`** instead of BeautifulSoup for better multi-line support
- `_html_to_image()` replaced with `_html_to_image_with_bbox()` that returns coordinates
- Increased wait time for JavaScript execution to ensure element marking completes
- Improved text normalization for better matching across HTML elements

### Fixed
- ✅ Inaccurate bounding box positioning with variable-width fonts
- ✅ **Incorrect positioning with multi-line text spans** - Now uses `window.find()` 
- ✅ **Text that crosses element boundaries** - JavaScript can find text across nodes
- ✅ Layout-dependent positioning issues
- ✅ Bounding boxes not aligned with actual text location
- ✅ `os.makedirs('')` error when output path has no directory component
- ✅ Invalid coordinate errors (y1 < y0) with coordinate validation

## [0.1.0] - 2024-12-19

### Added
- Initial release
- Extract images from markdown files and highlight text chunks with bounding boxes
- Support for adding scores to bounding boxes
- Command-line interface
- Python API for programmatic usage
