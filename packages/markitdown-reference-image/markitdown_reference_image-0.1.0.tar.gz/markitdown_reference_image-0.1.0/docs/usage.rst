Usage
=====

Basic Usage
-----------

.. code-block:: python

   from markitdown_reference_image import MarkitdownImageExtractor

   # Initialize the extractor
   extractor = MarkitdownImageExtractor()

   # Path to your markdown file
   markdown_file = "document.md"

   # Text chunk to find and highlight
   chunk_text = "target text that we want to find"

   # Extract image with highlighted text
   image_path = extractor.extract_with_highlight(
       markdown_file=markdown_file,
       chunk_text=chunk_text,
       output_path="highlighted_image.png"
   )

   print(f"Image saved to: {image_path}")

With Score
----------

.. code-block:: python

   # Extract image with highlighted text and score
   image_path = extractor.extract_with_highlight(
       markdown_file="document.md",
       chunk_text=chunk_text,
       output_path="highlighted_image_with_score.png",
       score=0.85  # Score to display in the bounding box
   )

Custom Styling
--------------

.. code-block:: python

   # Customize the bounding box appearance
   image_path = extractor.extract_with_highlight(
       markdown_file="document.md",
       chunk_text=chunk_text,
       output_path="custom_highlighted_image.png",
       score=0.92,
       box_color=(0, 255, 0),  # Green box
       box_width=5,            # Thicker box
       score_color=(255, 255, 0),  # Yellow text
       score_bg_color=(0, 0, 255)  # Blue background
   )
