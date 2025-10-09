"""
Core module for markitdown image extraction functionality.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Union

from .text_finder import TextFinder
from .image_processor import ImageProcessor


class MarkitdownImageExtractor:
    """
    Main class for extracting images from markdown files and highlighting text chunks.
    
    This class coordinates the process of:
    1. Finding text chunks in markdown content
    2. Rendering markdown to HTML and capturing as image
    3. Drawing bounding boxes around found text
    4. Saving the result
    """
    
    def __init__(self, font_size: int = 16, line_height: int = 24, char_width: int = 9):
        """
        Initialize the extractor with required components.
        
        Args:
            font_size: Base font size in pixels for positioning calculations
            line_height: Line height including spacing in pixels
            char_width: Approximate character width in pixels
        """
        self.text_finder = TextFinder()
        self.image_processor = ImageProcessor(font_size, line_height, char_width)
    
    def extract_with_highlight(
        self,
        markdown_file: Union[str, Path],
        chunk_text: str,
        output_path: Optional[Union[str, Path]] = None,
        score: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Extract image from markdown file and highlight the specified chunk.
        
        Args:
            markdown_file: Path to the markdown file
            chunk_text: The text chunk to find and highlight
            output_path: Path to save the output image. If None, uses temp file
            score: Optional score to display in the bounding box
            **kwargs: Additional arguments for image processing
            
        Returns:
            str: Path to the saved image file
            
        Raises:
            ValueError: If chunk_text is not found in markdown file
            FileNotFoundError: If markdown file or output directory doesn't exist
        """
        # Read the markdown file
        markdown_path = Path(markdown_file)
        if not markdown_path.exists():
            raise FileNotFoundError(f"Markdown file '{markdown_file}' not found")
        
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Normalize the chunk text for searching
        normalized_chunk = self.text_finder._normalize_text(chunk_text)
        
        # Check if the text exists in the markdown
        if normalized_chunk not in self.text_finder._normalize_text(markdown_content):
            raise ValueError(f"Chunk text '{chunk_text}' not found in markdown file")
        
        # Convert markdown to HTML with text highlighting
        try:
            html_content = self._markdown_to_html(markdown_content, chunk_text)
            # Capture image and get bounding box coordinates from the rendered page
            image_path, bbox_coords = self._html_to_image_with_bbox(html_content)
        except RuntimeError as e:
            raise RuntimeError(f"Image extraction failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during image extraction: {e}")
        
        # Draw bounding box using actual coordinates
        result_path = self.image_processor.draw_bounding_box_from_coords(
            image_path=image_path,
            bbox_coords=bbox_coords,
            output_path=output_path,
            score=score,
            **kwargs
        )
        
        # Clean up temporary files if we created them
        if output_path is None and image_path != result_path:
            try:
                os.unlink(image_path)
            except OSError:
                pass  # Ignore cleanup errors
        
        return result_path
    
    def _markdown_to_html(self, markdown_content: str, target_text: str = None) -> str:
        """
        Convert markdown content to HTML with optional text marking.
        Uses JavaScript to find and wrap text after page load for better multi-line support.
        
        Args:
            markdown_content: Raw markdown content
            target_text: Optional text to mark for positioning
            
        Returns:
            str: HTML content with JavaScript to mark target text
        """
        import markdown
        import json
        
        # Convert markdown to HTML
        html = markdown.markdown(markdown_content)
        
        # Prepare JavaScript to mark text (if provided)
        mark_script = ""
        if target_text:
            # Escape the target text for JavaScript
            escaped_target = json.dumps(target_text)
            
            mark_script = f"""
            <script>
                // Function to normalize text (remove extra whitespace, lowercase)
                function normalizeText(text) {{
                    return text.replace(/\\s+/g, ' ').trim().toLowerCase();
                }}
                
                // Function to strip markdown formatting characters
                function stripMarkdown(text) {{
                    return text
                        .replace(/\\*\\*(.+?)\\*\\*/g, '$1')  // Bold
                        .replace(/\\*(.+?)\\*/g, '$1')       // Italic
                        .replace(/__(.+?)__/g, '$1')         // Bold alt
                        .replace(/_(.+?)_/g, '$1')           // Italic alt
                        .replace(/`(.+?)`/g, '$1')           // Code
                        .replace(/~~(.+?)~~/g, '$1')         // Strikethrough
                        .replace(/^#+\\s+/gm, '')            // Headers
                        .replace(/^[0-9]+\\.\\s+/gm, '')     // Numbered lists
                        .replace(/^[-*+]\\s+/gm, '')         // Bullet lists
                        .replace(/\\[(.+?)\\]\\(.+?\\)/g, '$1') // Links
                        .trim();
                }}
                
                // Function to find and wrap text across nodes
                function highlightText(searchText) {{
                    // Strip markdown from search text
                    let cleanSearchText = stripMarkdown(searchText);
                    
                    // Replace newlines with spaces for searching
                    cleanSearchText = cleanSearchText.replace(/\\n/g, ' ').replace(/\\r/g, '');
                    
                    const normalized = normalizeText(cleanSearchText);
                    const bodyElement = document.body;
                    
                    // Get all text content
                    const fullText = bodyElement.innerText || bodyElement.textContent;
                    const normalizedFull = normalizeText(fullText);
                    
                    // Find position in normalized text
                    const startPos = normalizedFull.indexOf(normalized);
                    if (startPos === -1) {{
                        console.warn('Text not found. Searched for:', normalized);
                        console.warn('In text:', normalizedFull.substring(0, 500));
                        return false;
                    }}
                    
                    // Use window.find() to search and select the text
                    // This works across multiple DOM nodes
                    if (window.find) {{
                        // Clear any existing selection
                        if (window.getSelection) {{
                            window.getSelection().removeAllRanges();
                        }}
                        
                        // Split search text into smaller chunks if it contains line breaks
                        const searchVariants = [
                            cleanSearchText,
                            cleanSearchText.replace(/\\s+/g, ' '),  // Normalize whitespace
                            searchText.replace(/\\n/g, ' ')  // Original with newlines replaced
                        ];
                        
                        let found = false;
                        for (const variant of searchVariants) {{
                            if (variant && variant.trim()) {{
                                window.getSelection().removeAllRanges();
                                found = window.find(variant.trim(), false, false, false, false, false, false);
                                if (found) break;
                            }}
                        }}
                        
                        if (found && window.getSelection) {{
                            const selection = window.getSelection();
                            if (selection.rangeCount > 0) {{
                                const range = selection.getRangeAt(0);
                                
                                // Create a span to wrap the selection
                                const span = document.createElement('span');
                                span.id = 'highlight-target';
                                span.style.position = 'relative';
                                
                                try {{
                                    // Wrap the selected text
                                    range.surroundContents(span);
                                    return true;
                                }} catch (e) {{
                                    // If surroundContents fails (crosses element boundaries),
                                    // use a different approach
                                    const contents = range.extractContents();
                                    span.appendChild(contents);
                                    range.insertNode(span);
                                    return true;
                                }}
                            }}
                        }}
                    }}
                    
                    return false;
                }}
                
                // Wait for page to load, then highlight
                window.addEventListener('load', function() {{
                    setTimeout(function() {{
                        const found = highlightText({escaped_target});
                        if (!found) {{
                            console.warn('Could not find text to highlight:', {escaped_target});
                        }}
                    }}, 100);
                }});
            </script>
            """
        
        # Wrap in basic HTML structure for better rendering
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #333;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                #highlight-target {{
                    position: relative;
                    display: inline;
                }}
            </style>
            {mark_script}
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return full_html
    
    def _html_to_image_with_bbox(self, html_content: str) -> Tuple[str, Tuple[int, int, int, int]]:
        """
        Convert HTML to image and get bounding box coordinates of marked element.
        
        Args:
            html_content: HTML content with marked target element
            
        Returns:
            Tuple of (image_path, (left, top, right, bottom))
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as e:
            raise RuntimeError(f"Selenium not available: {e}")
        
        html_file_path = None
        driver = None
        
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file_path = f.name
            
            if not html_file_path or not os.path.exists(html_file_path):
                raise RuntimeError("Failed to create temporary HTML file")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1200,800')
            
            # Setup Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Load the HTML file
            file_url = f"file://{os.path.abspath(html_file_path)}"
            driver.get(file_url)
            
            # Wait for JavaScript to execute and mark the text
            # Give more time for the window.find() and DOM manipulation
            import time
            time.sleep(1)  # Wait for page load and JavaScript execution
            
            # Get bounding box coordinates of the marked element
            bbox_coords = None
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    target_element = driver.find_element(By.ID, "highlight-target")
                    location = target_element.location
                    size = target_element.size
                    
                    # Calculate bounding box
                    left = int(location['x'])
                    top = int(location['y'])
                    right = int(location['x'] + size['width'])
                    bottom = int(location['y'] + size['height'])
                    
                    bbox_coords = (left, top, right, bottom)
                    break
                except Exception as e:
                    if attempt < max_attempts - 1:
                        time.sleep(0.5)  # Wait a bit more
                    else:
                        # If we can't find the element after all attempts, return default coords
                        print(f"Warning: Could not find highlight-target element: {e}")
                        bbox_coords = (50, 50, 350, 100)
            
            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            
            if not screenshot:
                raise RuntimeError("Failed to capture screenshot")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                f.write(screenshot)
                image_path = f.name
            
            if not image_path or not os.path.exists(image_path):
                raise RuntimeError("Failed to save screenshot")
            
            return image_path, bbox_coords
                
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            
            if html_file_path and os.path.exists(html_file_path):
                try:
                    os.unlink(html_file_path)
                except OSError:
                    pass
    
    def _html_to_image(self, html_content: str) -> str:
        """
        Convert HTML content to image using Selenium.
        
        Args:
            html_content: HTML content to render
            
        Returns:
            str: Path to the generated image file
            
        Raises:
            RuntimeError: If Chrome/Selenium setup fails
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError as e:
            raise RuntimeError(f"Selenium not available: {e}. Please install with: pip install selenium webdriver-manager")
        
        # Create temporary HTML file
        html_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                html_file_path = f.name
            
            if not html_file_path or not os.path.exists(html_file_path):
                raise RuntimeError("Failed to create temporary HTML file")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1200,800')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            
            driver = None
            try:
                # Setup Chrome driver
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # Load the HTML file
                file_url = f"file://{os.path.abspath(html_file_path)}"
                driver.get(file_url)
                
                # Wait for page to load
                driver.implicitly_wait(3)
                
                # Take screenshot
                screenshot = driver.get_screenshot_as_png()
                
                if not screenshot:
                    raise RuntimeError("Failed to capture screenshot")
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    f.write(screenshot)
                    image_path = f.name
                
                if not image_path or not os.path.exists(image_path):
                    raise RuntimeError("Failed to save screenshot")
                
                return image_path
                    
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                
        except Exception as e:
            raise RuntimeError(f"Failed to convert HTML to image: {e}")
            
        finally:
            # Clean up HTML file
            if html_file_path and os.path.exists(html_file_path):
                try:
                    os.unlink(html_file_path)
                except OSError:
                    pass
