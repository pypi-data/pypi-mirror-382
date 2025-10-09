"""
Image processing module for drawing bounding boxes and adding scores.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Union, Tuple
from PIL import Image, ImageDraw, ImageFont


class ImageProcessor:
    """
    Handles image processing operations including drawing bounding boxes and adding scores.
    """
    
    def __init__(self, font_size: int = 16, line_height: int = 24, char_width: int = 9):
        """
        Initialize the image processor with default settings.
        
        Args:
            font_size: Base font size in pixels
            line_height: Line height including spacing in pixels
            char_width: Approximate character width in pixels
        """
        self.default_box_color = (255, 0, 0)  # Red
        self.default_box_width = 3
        self.default_score_color = (255, 255, 255)  # White
        self.default_score_bg_color = (0, 0, 0)  # Black
        self.font_size = font_size
        self.line_height = line_height
        self.char_width = char_width
    
    def draw_bounding_box(
        self,
        image_path: str,
        text_position,
        output_path: Optional[Union[str, Path]] = None,
        score: Optional[float] = None,
        box_color: Optional[Tuple[int, int, int]] = None,
        box_width: Optional[int] = None,
        score_color: Optional[Tuple[int, int, int]] = None,
        score_bg_color: Optional[Tuple[int, int, int]] = None,
        **kwargs
    ) -> str:
        """
        Draw a bounding box around the specified text position and optionally add a score.
        
        Args:
            image_path: Path to the input image
            text_position: TextPosition object containing position information
            output_path: Path to save the output image. If None, uses temp file
            score: Optional score to display in the top-right corner of the box
            box_color: Color of the bounding box (R, G, B)
            box_width: Width of the bounding box lines
            score_color: Color of the score text
            score_bg_color: Background color of the score box
            **kwargs: Additional arguments
            
        Returns:
            str: Path to the saved image file
        """
        # Load the image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Set default values
        box_color = box_color or self.default_box_color
        box_width = box_width or self.default_box_width
        score_color = score_color or self.default_score_color
        score_bg_color = score_bg_color or self.default_score_bg_color
        
        # Calculate bounding box coordinates
        # Note: This is a simplified approach. In a real implementation,
        # you would need to map the text position to actual pixel coordinates
        # based on the rendered HTML layout
        bbox_coords = self._calculate_bbox_coordinates(
            image, text_position, **kwargs
        )
        
        # Draw the bounding box
        self._draw_box(draw, bbox_coords, box_color, box_width)
        
        # Add score if provided
        if score is not None:
            self._draw_score(
                draw, bbox_coords, score, score_color, score_bg_color
            )
        
        # Determine output path
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                output_path = f.name
        else:
            output_path = str(output_path)
            # Ensure output directory exists (only if there's a directory path)
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there's actually a directory path
                os.makedirs(output_dir, exist_ok=True)
        
        # Save the image
        image.save(output_path)
        return output_path
    
    def draw_bounding_box_from_coords(
        self,
        image_path: str,
        bbox_coords: Tuple[int, int, int, int],
        output_path: Optional[str] = None,
        score: Optional[float] = None,
        box_color: Optional[Tuple[int, int, int]] = None,
        box_width: Optional[int] = None,
        score_color: Optional[Tuple[int, int, int]] = None,
        score_bg_color: Optional[Tuple[int, int, int]] = None,
        **kwargs
    ) -> str:
        """
        Draw a bounding box on an image using provided coordinates.
        
        Args:
            image_path: Path to the input image
            bbox_coords: Tuple of (left, top, right, bottom) coordinates
            output_path: Path to save the output image
            score: Optional score to display
            box_color: RGB color for the box
            box_width: Width of the box lines
            score_color: RGB color for score text
            score_bg_color: RGB background color for score
            
        Returns:
            str: Path to the output image
        """
        # Load the image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Use provided colors or defaults
        box_color = box_color or self.default_box_color
        box_width = box_width if box_width is not None else self.default_box_width
        score_color = score_color or self.default_score_color
        score_bg_color = score_bg_color or self.default_score_bg_color
        
        # Add some padding to the coordinates
        padding = 5
        left, top, right, bottom = bbox_coords
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(image.width, right + padding)
        bottom = min(image.height, bottom + padding)
        
        # Validate coordinates
        if left >= right:
            right = left + 50  # Ensure minimum width
        if top >= bottom:
            bottom = top + 20  # Ensure minimum height
        
        # Final bounds check
        left = max(0, min(left, image.width - 10))
        top = max(0, min(top, image.height - 10))
        right = max(left + 10, min(right, image.width))
        bottom = max(top + 10, min(bottom, image.height))
        
        coords = (left, top, right, bottom)
        
        # Draw the bounding box
        self._draw_box(draw, coords, box_color, box_width)
        
        # Draw score if provided
        if score is not None:
            self._draw_score(
                draw, coords, score, score_color, score_bg_color
            )
        
        # Determine output path
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                output_path = f.name
        else:
            output_path = str(output_path)
            # Ensure output directory exists (only if there's a directory path)
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        
        # Save the image
        image.save(output_path)
        return output_path
    
    def _calculate_bbox_coordinates(
        self, 
        image: Image.Image, 
        text_position,
        **kwargs
    ) -> Tuple[int, int, int, int]:
        """
        Calculate bounding box coordinates based on text position.
        
        This implementation uses a more sophisticated approach:
        1. Estimates text position based on line numbers and character positions
        2. Uses font metrics to calculate approximate pixel positions
        3. Handles multi-line text spans
        
        Args:
            image: The PIL Image object
            text_position: TextPosition object
            
        Returns:
            Tuple of (left, top, right, bottom) coordinates
        """
        width, height = image.size
        
        # Use configurable font metrics
        font_size = self.font_size
        line_height = self.line_height
        char_width = self.char_width
        margin_left = 20  # Left margin
        margin_top = 20  # Top margin
        
        # Calculate position based on line and column
        # Start position
        start_x = margin_left + (text_position.start_column * char_width)
        start_y = margin_top + (text_position.start_line * line_height)
        
        # End position
        end_x = margin_left + (text_position.end_column * char_width)
        end_y = margin_top + (text_position.end_line * line_height)
        
        # For single line text, use the end column for width
        if text_position.start_line == text_position.end_line:
            # Single line - use character width for bounding box
            left = start_x
            top = start_y
            right = end_x
            bottom = start_y + line_height
        else:
            # Multi-line text - create a wider bounding box
            left = start_x
            top = start_y
            right = width - margin_left  # Extend to right margin
            bottom = end_y + line_height
        
        # Add some padding around the text
        padding = 5
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(width, right + padding)
        bottom = min(height, bottom + padding)
        
        # Ensure minimum size
        min_width = 50
        min_height = 20
        if right - left < min_width:
            center_x = (left + right) // 2
            left = max(0, center_x - min_width // 2)
            right = min(width, center_x + min_width // 2)
        
        if bottom - top < min_height:
            center_y = (top + bottom) // 2
            top = max(0, center_y - min_height // 2)
            bottom = min(height, center_y + min_height // 2)
        
        return (left, top, right, bottom)
    
    def _draw_box(
        self, 
        draw: ImageDraw.Draw, 
        coords: Tuple[int, int, int, int], 
        color: Tuple[int, int, int], 
        width: int
    ):
        """
        Draw a bounding box on the image.
        
        Args:
            draw: PIL ImageDraw object
            coords: Bounding box coordinates (left, top, right, bottom)
            color: Box color (R, G, B)
            width: Box line width
        """
        left, top, right, bottom = coords
        
        # Draw rectangle outline
        for i in range(width):
            draw.rectangle(
                [left + i, top + i, right - i, bottom - i],
                outline=color
            )
    
    def _draw_score(
        self, 
        draw: ImageDraw.Draw, 
        coords: Tuple[int, int, int, int], 
        score: float, 
        text_color: Tuple[int, int, int], 
        bg_color: Tuple[int, int, int]
    ):
        """
        Draw a score in the top-right corner of the bounding box.
        
        Args:
            draw: PIL ImageDraw object
            coords: Bounding box coordinates
            score: Score value to display
            text_color: Text color (R, G, B)
            bg_color: Background color (R, G, B)
        """
        left, top, right, bottom = coords
        
        # Format the score
        score_text = f"{score:.2f}"
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except OSError:
            try:
                font = ImageFont.load_default()
            except OSError:
                font = None
        
        # Calculate text size
        if font:
            bbox = draw.textbbox((0, 0), score_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(score_text) * 8
            text_height = 16
        
        # Position score in top-right corner of bounding box
        score_x = right - text_width - 10
        score_y = top - text_height - 5
        
        # Draw background rectangle
        bg_coords = [
            score_x - 5, score_y - 2,
            score_x + text_width + 5, score_y + text_height + 2
        ]
        draw.rectangle(bg_coords, fill=bg_color)
        
        # Draw score text
        draw.text((score_x, score_y), score_text, fill=text_color, font=font)
    
    def batch_process(
        self,
        image_paths: list,
        text_positions: list,
        output_dir: Union[str, Path],
        **kwargs
    ) -> list:
        """
        Process multiple images with their corresponding text positions.
        
        Args:
            image_paths: List of input image paths
            text_positions: List of TextPosition objects
            output_dir: Directory to save output images
            **kwargs: Additional arguments for processing
            
        Returns:
            List of output image paths
        """
        output_paths = []
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, (image_path, text_position) in enumerate(zip(image_paths, text_positions)):
            output_path = output_dir / f"processed_{i:03d}.png"
            result_path = self.draw_bounding_box(
                image_path, text_position, output_path, **kwargs
            )
            output_paths.append(result_path)
        
        return output_paths
