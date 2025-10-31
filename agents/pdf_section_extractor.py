"""
PDF Section Extractor Agent
Reads PDF files and extracts a specific section based on section title (e.g., "Introduction", "Related Work").
Uses AI API to accurately identify section boundaries.
"""

from typing import List, Dict, Optional
import re
import os
import json

# Try to import PDF parsing libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Try to import Google Gen AI SDK
try:
    from google.genai import Client as GenAIClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class PDFSectionExtractorAgent:
    """Agent that extracts sections from PDF files."""
    
    def __init__(self, name: str = "PDF Section Extractor", 
                 gemini_api_key: Optional[str] = None,
                 use_ai: bool = True):
        """
        Initialize PDF Section Extractor Agent.
        
        Args:
            name: Name of the agent
            gemini_api_key: Optional Gemini API key for AI-powered section detection.
                          If not provided, will try GEMINI_API_KEY env variable.
            use_ai: Whether to use AI API for better section boundary detection (default: True)
        """
        self.name = name
        self.extraction_history = []
        self.use_ai = use_ai
        
        # Setup AI API if requested
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_client = None
        
        if self.use_ai and GEMINI_AVAILABLE and self.gemini_api_key:
            try:
                self.gemini_client = GenAIClient(api_key=self.gemini_api_key)
                print(f"✓ AI-powered section extraction enabled (using Gemini API)")
            except Exception as e:
                print(f"Warning: Failed to configure Gemini API: {e}")
                print("  Falling back to rule-based extraction")
                self.use_ai = False
        elif self.use_ai and not GEMINI_AVAILABLE:
            print("Note: google-genai not installed. Install with: pip install google-genai")
            print("  Using rule-based extraction")
            self.use_ai = False
        elif self.use_ai and not self.gemini_api_key:
            print("Note: No Gemini API key provided. Set GEMINI_API_KEY environment variable for AI-powered extraction")
            print("  Using rule-based extraction")
            self.use_ai = False
        
        # Check if PDF libraries are available
        if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            print("Warning: No PDF parsing library available. Install pdfplumber or PyPDF2.")
            print("  Install with: pip install pdfplumber  (recommended)")
            print("  Or: pip install PyPDF2")
    
    def extract_section(self, pdf_path: str, section_title: str) -> str:
        """
        Extract a specific section from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            section_title: Title of the section to extract (e.g., "Introduction", "Related Work")
        
        Returns:
            Extracted content of the section as a string
        
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If section not found or extraction fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(pdf_path)
        
        if not text:
            raise ValueError(f"Failed to extract text from PDF: {pdf_path}")
        
        # Extract the specific section (use AI if available)
        if self.use_ai and self.gemini_client:
            section_content = self._extract_section_with_ai(text, section_title, pdf_path)
        else:
            section_content = self._extract_section_by_title(text, section_title)
        
        if not section_content:
            raise ValueError(f"Section '{section_title}' not found in PDF: {pdf_path}")
        
        # Store in history
        self.extraction_history.append({
            "pdf_path": pdf_path,
            "section_title": section_title,
            "content_length": len(section_content)
        })
        
        return section_content
    
    def _extract_section_with_ai(self, text: str, section_title: str, pdf_path: str) -> str:
        """
        Use AI API to accurately extract a section from the PDF text.
        
        Args:
            text: Full text extracted from PDF
            section_title: Title of the section to extract
            pdf_path: Path to PDF file (for context)
            
        Returns:
            Extracted section content
        """
        if not self.gemini_client:
            return ""
        
        # Truncate text if too long (keep first 50000 chars which should be enough for intro)
        # For Introduction, it's typically early in the paper, so this should be sufficient
        text_to_analyze = text[:50000] if len(text) > 50000 else text
        
        prompt = f"""You are analyzing an academic research paper. Extract ONLY the "{section_title}" section content.

The "{section_title}" section header may appear in various formats:
- "{section_title}"
- "1 {section_title}" or "1. {section_title}"
- "{section_title.upper()}"
- The section header might appear mid-line due to PDF formatting

CRITICAL INSTRUCTIONS:
1. Find where the {section_title} section STARTS. Look for the section header which may appear:
   - At the start of a line
   - Mid-line (e.g., "previous text 1 INTRODUCTION" where "1 INTRODUCTION" is the header)
   - In various formats and cases

2. Extract ALL content from the {section_title} section starting from the FIRST MEANINGFUL SENTENCE.
   - If the header appears mid-line, skip everything before "1 INTRODUCTION" or "{section_title.upper()}"
   - Start from the actual content, not the header

3. STOP extracting when you reach the NEXT section. Signs of the next section:
   - Headers like "Related Work", "Background", "Methodology", "2", "2.1", "2 RELATED WORK", etc.
   - Numbered sections that are NOT part of {section_title}

4. Do NOT include:
   - The section header itself (e.g., "1 INTRODUCTION", "INTRODUCTION")
   - Any content from Abstract or previous sections
   - Any content from sections that come after {section_title}
   - Metadata, author information, or formatting artifacts

5. The {section_title} section typically contains:
   - Introduction to the topic
   - Background and motivation
   - Problem statement
   - Research objectives
   - Paper contributions or overview

6. **IMPORTANT: Handle text wrapping from PDF extraction:**
   - The extracted text may have unwanted line breaks in the middle of paragraphs and sentences
   - Words may be broken across lines (e.g., "research op-" on one line followed by "portunities" on the next)
   - Sentences may be broken across multiple lines
   - You must reconstruct proper paragraphs by:
     a. Joining broken words that are split across line breaks (e.g., "op-" + "portunities" → "opportunities")
     b. Merging lines that belong to the same sentence (end lines with a hyphen or no punctuation should connect to next line)
     c. Preserving only intentional paragraph breaks (double newlines or clear paragraph boundaries)
     d. Ensuring sentences flow naturally without mid-sentence line breaks
     e. Adding appropriate spacing between sentences within paragraphs
   - The final output should have clean, readable paragraphs with proper sentence boundaries

Here is the paper text:

{text_to_analyze}

Extract and return ONLY the complete {section_title} section content with proper paragraph formatting.
- Start from the first meaningful sentence after "1 INTRODUCTION" or "{section_title.upper()}" header.
- End when the next major section begins (typically "2" or "Related Work" or similar).
- Fix all text wrapping issues: join broken words, merge sentence fragments, and format as clean paragraphs."""

        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                section_content = response.text.strip()
                
                # Clean up any AI-added explanations
                # Remove common AI prefixes
                cleanup_patterns = [
                    r'^The\s+Introduction\s+section\s+is:?\s*',
                    r'^Here\s+is\s+the\s+Introduction\s+section:?\s*',
                    r'^The\s+extracted\s+content:?\s*',
                ]
                for pattern in cleanup_patterns:
                    section_content = re.sub(pattern, '', section_content, flags=re.IGNORECASE)
                section_content = section_content.strip()
                
                # If result is too short or empty, might have failed
                if not section_content or len(section_content) < 100:
                    print(f"Warning: AI extraction returned very short content ({len(section_content)} chars)")
                    print("  Falling back to rule-based extraction")
                    return self._extract_section_by_title(text, section_title)
                
                return section_content
        except Exception as e:
            print(f"Warning: AI extraction failed: {e}")
            print("  Falling back to rule-based extraction")
            # Fall back to rule-based
            return self._extract_section_by_title(text, section_title)
        
        return ""
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        Tries pdfplumber first (better), falls back to PyPDF2.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        # Try pdfplumber first (better text extraction)
        if PDFPLUMBER_AVAILABLE:
            try:
                text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
            except Exception as e:
                print(f"Warning: pdfplumber failed: {e}. Trying PyPDF2...")
        
        # Fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                text = ""
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except Exception as e:
                print(f"Error: PyPDF2 failed: {e}")
                return ""
        
        raise ImportError("No PDF parsing library available. Install pdfplumber or PyPDF2.")
    
    def _get_common_section_titles(self) -> List[str]:
        """Get common academic paper section titles."""
        return [
            "Abstract",
            "Introduction",
            "Related Work",
            "Literature Review",
            "Background",
            "Methodology",
            "Methods",
            "Approach",
            "Results",
            "Findings",
            "Discussion",
            "Evaluation",
            "Experiments",
            "Conclusion",
            "Conclusions",
            "Future Work",
            "Acknowledgments",
            "References",
            "Bibliography"
        ]
    
    def _extract_section_by_title(self, text: str, section_title: str) -> str:
        """
        Extract a specific section from text based on section title.
        
        Args:
            text: Full text content
            section_title: Title of the section to find
            
        Returns:
            Extracted content of the section as a string, or empty string if not found
        """
        lines = text.split('\n')
        
        # Create patterns to match section headers
        # Try different formats: "Introduction", "1. Introduction", "INTRODUCTION", etc.
        patterns = [
            rf'^\s*{re.escape(section_title)}\s*:?\s*$',  # "Introduction:" or "Introduction"
            rf'^\s*\d+\.?\s*{re.escape(section_title)}\s*:?\s*$',  # "1. Introduction" or "1 Introduction"
            rf'^\s*\d+\.\d+\.?\s*{re.escape(section_title)}\s*:?\s*$',  # "1.1 Introduction"
            rf'^\s*\d+\.\d+\.\d+\.?\s*{re.escape(section_title)}\s*:?\s*$',  # "1.1.1 Introduction"
            rf'^\s*{re.escape(section_title.upper())}\s*:?\s*$',  # "INTRODUCTION"
            rf'^\s*\d+\.?\s*{re.escape(section_title.upper())}\s*:?\s*$',  # "1. INTRODUCTION"
            rf'^\s*#{1,3}\s*{re.escape(section_title)}\s*:?\s*$',  # "# Introduction" (markdown style)
        ]
        
        # Find the section header
        # First try exact line matches (headers at start of line)
        section_start_pos = None
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            for pattern in patterns:
                if re.match(pattern, line_stripped, re.IGNORECASE):
                    section_start_pos = i
                    break
            if section_start_pos is not None:
                break
        
        # If not found at start of line, search for section title anywhere in the line
        # This handles cases where "1 INTRODUCTION" appears mid-line due to PDF formatting
        if section_start_pos is None:
            # Patterns that can appear anywhere in line
            anywhere_patterns = [
                rf'\b\d+\s+{re.escape(section_title.upper())}\b',  # "1 INTRODUCTION"
                rf'\b\d+\.\s+{re.escape(section_title.upper())}\b',  # "1. INTRODUCTION"
                rf'\b\d+\s+{re.escape(section_title)}\b',  # "1 Introduction"
                rf'\b\d+\.\s+{re.escape(section_title)}\b',  # "1. Introduction"
                rf'\b{re.escape(section_title.upper())}\b',  # "INTRODUCTION" anywhere
            ]
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                for pattern in anywhere_patterns:
                    match = re.search(pattern, line_stripped, re.IGNORECASE)
                    if match:
                        # Found the section header
                        # If it's at the end of the line, start from next line
                        # Otherwise, try to extract from after the header
                        match_end = match.end()
                        if match_end >= len(line_stripped) - 2:  # At or near end of line
                            section_start_pos = i + 1
                        else:
                            # Header is in middle of line, extract remainder and continue
                            section_start_pos = i
                        break
                if section_start_pos is not None:
                    break
        
        if section_start_pos is None:
            return ""
        
        # Find the next section or end of document
        # Look for other common section headers after this one
        common_sections = self._get_common_section_titles()
        section_end_pos = len(lines)
        
        for i in range(section_start_pos + 1, len(lines)):
            line_stripped = lines[i].strip()
            
            # Check if this line looks like another section header
            # (not the same as the one we're looking for)
            for common_section in common_sections:
                if common_section.lower() == section_title.lower():
                    continue
                
                # Check if this line matches a different section header pattern
                common_patterns = [
                    rf'^\s*{re.escape(common_section)}\s*:?\s*$',
                    rf'^\s*\d+\.?\s*{re.escape(common_section)}\s*:?\s*$',
                    rf'^\s*\d+\.\d+\.?\s*{re.escape(common_section)}\s*:?\s*$',
                    rf'^\s*{re.escape(common_section.upper())}\s*:?\s*$',
                ]
                
                for pattern in common_patterns:
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        section_end_pos = i
                        break
                
                if section_end_pos < len(lines):
                    break
            
            if section_end_pos < len(lines):
                break
            
            # Also check for numbered sections that might indicate a new section
            # Pattern: "1.", "1.1", "2.", etc. at start of line (but not too close to start)
            if i > section_start_pos + 3:  # Give some buffer
                numbered_pattern = r'^\s*\d+\.?\s+[A-Z]'  # Number followed by capital letter
                if re.match(numbered_pattern, line_stripped):
                    # Check if it's not just continuing the current section
                    # (too many words = likely continuation, not new section)
                    word_count = len(line_stripped.split())
                    if word_count < 10:  # Short lines are likely headers
                        section_end_pos = i
                        break
        
        # Extract section content
        section_lines = lines[section_start_pos:section_end_pos]
        section_content = '\n'.join(section_lines).strip()
        
        # Remove the header line itself if it appears at the start
        # Try to remove the section title from the start
        header_pattern = rf'^{re.escape(section_title)}.*?\n'
        section_content = re.sub(header_pattern, '', section_content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Also try numbered patterns at start of content
        numbered_header_pattern = rf'^\d+\.?\s*{re.escape(section_title)}.*?\n'
        section_content = re.sub(numbered_header_pattern, '', section_content, flags=re.IGNORECASE | re.MULTILINE)
        
        # If section title appears mid-line in first line, extract text after it
        first_line = section_lines[0] if section_lines else ""
        for pattern in [
            rf'.*?\d+\s+{re.escape(section_title.upper())}\s*(.*)$',
            rf'.*?\d+\.\s+{re.escape(section_title.upper())}\s*(.*)$',
            rf'.*?{re.escape(section_title.upper())}\s*(.*)$',
        ]:
            match = re.search(pattern, first_line, re.IGNORECASE)
            if match:
                # Replace first line with content after header
                remaining_text = match.group(1).strip()
                if remaining_text:
                    section_lines[0] = remaining_text
                    section_content = '\n'.join(section_lines).strip()
                else:
                    # Header at end of line, skip first line
                    if len(section_lines) > 1:
                        section_content = '\n'.join(section_lines[1:]).strip()
                break
        
        # Clean up leading whitespace
        section_content = section_content.strip()
        
        return section_content
    
    
    def get_extraction_history(self) -> List[Dict]:
        """Get history of all extractions."""
        return self.extraction_history

