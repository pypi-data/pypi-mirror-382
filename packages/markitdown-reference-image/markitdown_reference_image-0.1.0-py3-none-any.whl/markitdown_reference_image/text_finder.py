"""
Text finding module for locating text chunks in markdown content.
"""

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class TextPosition:
    """Represents the position of found text in the document."""
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    text: str
    context: str  # Surrounding context for better positioning


class TextFinder:
    """
    Handles finding text chunks in markdown content and determining their positions.
    """
    
    def __init__(self):
        """Initialize the text finder."""
        pass
    
    def find_text_position(
        self, 
        markdown_content: str, 
        chunk_text: str
    ) -> Optional[TextPosition]:
        """
        Find the position of a text chunk in markdown content.
        
        Args:
            markdown_content: The full markdown content
            chunk_text: The text chunk to find
            
        Returns:
            TextPosition if found, None otherwise
        """
        # Clean and normalize both texts for better matching
        normalized_chunk = self._normalize_text(chunk_text)
        lines = markdown_content.split('\n')
        
        # First, try to find the text as a single line
        for i, line in enumerate(lines):
            if normalized_chunk in self._normalize_text(line):
                return self._create_text_position(
                    lines, i, normalized_chunk, chunk_text
                )
        
        # If not found as single line, try multi-line search
        multi_line_result = self._find_multiline_text(lines, normalized_chunk, chunk_text)
        if multi_line_result:
            return multi_line_result
        
        # Try fuzzy matching if exact match fails
        return self._fuzzy_find_text(lines, normalized_chunk, chunk_text)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for better matching by removing extra whitespace, markdown formatting, and normalizing case.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Strip markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # Italic
        text = re.sub(r'__(.+?)__', r'\1', text)      # Bold alt
        text = re.sub(r'_(.+?)_', r'\1', text)        # Italic alt
        text = re.sub(r'`(.+?)`', r'\1', text)        # Code
        text = re.sub(r'~~(.+?)~~', r'\1', text)      # Strikethrough
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # Headers
        text = re.sub(r'^[0-9]+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
        text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)  # Bullet lists
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Links
        
        # Remove extra whitespace and normalize
        normalized = re.sub(r'\s+', ' ', text.strip())
        return normalized.lower()
    
    def _find_multiline_text(
        self, 
        lines: List[str], 
        normalized_chunk: str, 
        original_chunk: str
    ) -> Optional[TextPosition]:
        """
        Find text that spans multiple lines.
        
        Args:
            lines: All lines of the document
            normalized_chunk: Normalized chunk text
            original_chunk: Original chunk text
            
        Returns:
            TextPosition if found, None otherwise
        """
        # Join lines with spaces to create a continuous text
        full_text = ' '.join(lines)
        normalized_full = self._normalize_text(full_text)
        
        if normalized_chunk in normalized_full:
            # Find the position in the full text
            start_pos = normalized_full.find(normalized_chunk)
            end_pos = start_pos + len(normalized_chunk)
            
            # Map back to line and column positions
            current_pos = 0
            start_line = 0
            start_column = 0
            end_line = 0
            end_column = 0
            
            for i, line in enumerate(lines):
                line_length = len(self._normalize_text(line)) + 1  # +1 for space
                
                if current_pos <= start_pos < current_pos + line_length:
                    start_line = i
                    start_column = start_pos - current_pos
                
                if current_pos <= end_pos <= current_pos + line_length:
                    end_line = i
                    end_column = end_pos - current_pos
                    break
                
                current_pos += line_length
            
            # Get context
            context_lines = []
            for i in range(max(0, start_line - 2), min(len(lines), end_line + 3)):
                if i < start_line or i > end_line:
                    context_lines.append(lines[i])
            
            return TextPosition(
                start_line=start_line,
                end_line=end_line,
                start_column=start_column,
                end_column=end_column,
                text=original_chunk,
                context='\n'.join(context_lines)
            )
        
        return None
    
    def _create_text_position(
        self, 
        lines: List[str], 
        line_index: int, 
        normalized_chunk: str,
        original_chunk: str
    ) -> TextPosition:
        """
        Create a TextPosition object from found text.
        
        Args:
            lines: All lines of the document
            line_index: Index of the line containing the text
            normalized_chunk: Normalized chunk text
            original_chunk: Original chunk text
            
        Returns:
            TextPosition object
        """
        line = lines[line_index]
        normalized_line = self._normalize_text(line)
        
        # Find the start and end positions within the line
        start_pos = normalized_line.find(normalized_chunk)
        end_pos = start_pos + len(normalized_chunk)
        
        # Get context (previous and next lines)
        context_lines = []
        for i in range(max(0, line_index - 2), min(len(lines), line_index + 3)):
            if i != line_index:
                context_lines.append(lines[i])
        
        context = '\n'.join(context_lines)
        
        return TextPosition(
            start_line=line_index,
            end_line=line_index,
            start_column=start_pos,
            end_column=end_pos,
            text=original_chunk,
            context=context
        )
    
    def _fuzzy_find_text(
        self, 
        lines: List[str], 
        normalized_chunk: str, 
        original_chunk: str
    ) -> Optional[TextPosition]:
        """
        Perform fuzzy matching to find text that might be split across lines or slightly different.
        
        Args:
            lines: All lines of the document
            normalized_chunk: Normalized chunk text to find
            original_chunk: Original chunk text
            
        Returns:
            TextPosition if found, None otherwise
        """
        # Join all lines and try to find the chunk
        full_text = ' '.join(lines)
        normalized_full = self._normalize_text(full_text)
        
        if normalized_chunk in normalized_full:
            # Find which line contains the start of the match
            chunk_words = normalized_chunk.split()
            if len(chunk_words) > 0:
                first_word = chunk_words[0]
                
                for i, line in enumerate(lines):
                    if first_word in self._normalize_text(line):
                        return self._create_text_position(
                            lines, i, normalized_chunk, original_chunk
                        )
        
        return None
    
    def find_multiple_chunks(
        self, 
        markdown_content: str, 
        chunk_texts: List[str]
    ) -> List[TextPosition]:
        """
        Find multiple text chunks in markdown content.
        
        Args:
            markdown_content: The full markdown content
            chunk_texts: List of text chunks to find
            
        Returns:
            List of TextPosition objects for found chunks
        """
        positions = []
        for chunk_text in chunk_texts:
            position = self.find_text_position(markdown_content, chunk_text)
            if position:
                positions.append(position)
        
        return positions
