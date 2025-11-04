"""
Plain Text Extractor Utility
Extracts sections from PDF files. Can extract a single section or all sections.
Saves extracted sections as text files to the extracted_sections folder.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
import re

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


class PlainTextExtractor:
    """Utility to extract sections from PDF files."""
    
    def __init__(self, output_base_dir: str = "extracted_sections",
                 gemini_api_key: Optional[str] = None,
                 use_ai: bool = True):
        """
        Initialize PlainTextExtractor utility.
        
        Args:
            output_base_dir: Base directory for extracted sections (default: "extracted_sections")
            gemini_api_key: Optional Gemini API key for AI-powered extraction
            use_ai: Whether to use AI for extraction (default: True)
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
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
        
        # Common section titles in order
        self.section_titles = [
            "Abstract",
            "Introduction",
            "Related Work",
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
            "References"
        ]
    
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
    
    def extract_all_sections(self, pdf_path: str, paper_name: Optional[str] = None,
                            gemini_api_key: Optional[str] = None, use_ai: Optional[bool] = None) -> Dict:
        """
        Extract all sections from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            paper_name: Name for the paper (default: derived from PDF filename)
            gemini_api_key: Optional Gemini API key (overrides instance setting)
            use_ai: Whether to use AI for extraction (overrides instance setting)
            
        Returns:
            Dictionary mapping section numbers to extracted file paths
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Override instance settings if provided
        if gemini_api_key is not None:
            self.gemini_api_key = gemini_api_key
            if self.use_ai and GEMINI_AVAILABLE and self.gemini_api_key:
                try:
                    self.gemini_client = GenAIClient(api_key=self.gemini_api_key)
                except Exception:
                    self.gemini_client = None
        
        if use_ai is not None:
            self.use_ai = use_ai
        
        # Determine paper name from PDF filename if not provided
        if paper_name is None:
            paper_name = Path(pdf_path).stem
        
        # Create subdirectory for this paper
        paper_dir = self.output_base_dir / paper_name
        paper_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_files = {}
        section_num = 1
        
        print(f"Extracting sections from: {pdf_path}")
        print(f"Output directory: {paper_dir}")
        print("-" * 60)
        
        # Extract each section
        for section_title in self.section_titles:
            try:
                print(f"\n[{section_num}] Extracting '{section_title}'...")
                content = self.extract_section(pdf_path, section_title)
                
                if content and len(content.strip()) > 0:
                    # Create filename: 1_abstract.txt, 2_introduction.txt, etc.
                    safe_title = section_title.lower().replace(' ', '_')
                    filename = f"{section_num}_{safe_title}.txt"
                    filepath = paper_dir / filename
                    
                    # Save to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    extracted_files[section_num] = {
                        'title': section_title,
                        'file': str(filepath),
                        'length': len(content)
                    }
                    
                    print(f"  ✓ Saved: {filename} ({len(content)} chars)")
                    section_num += 1
                else:
                    print(f"  - Section not found or empty")
            except ValueError:
                # Section not found, skip it
                print(f"  - Section not found")
                continue
            except Exception as e:
                print(f"  ✗ Error extracting '{section_title}': {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"Extraction complete! Extracted {len(extracted_files)} sections.")
        print(f"Output directory: {paper_dir}")
        
        return extracted_files
    
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
        
        # Increase text length for AI analysis (150000 chars for better completeness)
        max_text_length = 150000
        text_to_analyze = text[:max_text_length] if len(text) > max_text_length else text
        
        prompt = f"""You are analyzing an academic research paper. Extract ONLY the COMPLETE "{section_title}" section content.

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
   - DO NOT truncate - extract the COMPLETE section

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

Extract and return ONLY the COMPLETE {section_title} section content with proper paragraph formatting.
- Start from the first meaningful sentence after "1 INTRODUCTION" or "{section_title.upper()}" header.
- End when the next major section begins (typically "2" or "Related Work" or similar).
- Fix all text wrapping issues: join broken words, merge sentence fragments, and format as clean paragraphs.
- DO NOT truncate the content - extract the ENTIRE section."""

        try:
            # Try gemini-2.0-flash-exp first, then fallback to gemini-2.5-flash
            model_name = "gemini-2.0-flash-exp"
            try:
                response = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"max_output_tokens": 8192}
                )
            except Exception:
                # Fallback to gemini-2.5-flash
                model_name = "gemini-2.5-flash"
                response = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config={"max_output_tokens": 8192}
                )
            
            if response and hasattr(response, 'text') and response.text:
                section_content = response.text.strip()
                
                # Clean up any AI-added explanations
                cleanup_patterns = [
                    rf'^The\s+{re.escape(section_title)}\s+section\s+is:?\s*',
                    rf'^Here\s+is\s+the\s+{re.escape(section_title)}\s+section:?\s*',
                    r'^The\s+extracted\s+content:?\s*',
                ]
                for pattern in cleanup_patterns:
                    section_content = re.sub(pattern, '', section_content, flags=re.IGNORECASE)
                section_content = section_content.strip()
                
                # If result is too short, fallback to rule-based
                if not section_content or len(section_content) < 100:
                    print(f"Warning: AI extraction returned very short content ({len(section_content)} chars)")
                    print("  Falling back to rule-based extraction")
                    rule_based_content = self._extract_section_by_title(text, section_title)
                    # Use the longer result
                    if len(rule_based_content) > len(section_content):
                        return rule_based_content
                    return section_content
                
                return section_content
        except Exception as e:
            print(f"Warning: AI extraction failed: {e}")
            print("  Falling back to rule-based extraction")
            return self._extract_section_by_title(text, section_title)
        
        return ""
    
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
        patterns = [
            rf'^\s*{re.escape(section_title)}\s*:?\s*$',
            rf'^\s*\d+\.?\s*{re.escape(section_title)}\s*:?\s*$',
            rf'^\s*\d+\.\d+\.?\s*{re.escape(section_title)}\s*:?\s*$',
            rf'^\s*\d+\.\d+\.\d+\.?\s*{re.escape(section_title)}\s*:?\s*$',
            rf'^\s*{re.escape(section_title.upper())}\s*:?\s*$',
            rf'^\s*\d+\.?\s*{re.escape(section_title.upper())}\s*:?\s*$',
            rf'^\s*#{1,3}\s*{re.escape(section_title)}\s*:?\s*$',
        ]
        
        # Find the section header
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
        if section_start_pos is None:
            anywhere_patterns = [
                rf'\b\d+\s+{re.escape(section_title.upper())}\b',
                rf'\b\d+\.\s+{re.escape(section_title.upper())}\b',
                rf'\b\d+\s+{re.escape(section_title)}\b',
                rf'\b\d+\.\s+{re.escape(section_title)}\b',
                rf'\b{re.escape(section_title.upper())}\b',
            ]
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                for pattern in anywhere_patterns:
                    match = re.search(pattern, line_stripped, re.IGNORECASE)
                    if match:
                        match_end = match.end()
                        if match_end >= len(line_stripped) - 2:
                            section_start_pos = i + 1
                        else:
                            section_start_pos = i
                        break
                if section_start_pos is not None:
                    break
        
        if section_start_pos is None:
            return ""
        
        # Find the next section or end of document
        common_sections = self._get_common_section_titles()
        section_end_pos = len(lines)
        
        for i in range(section_start_pos + 1, len(lines)):
            line_stripped = lines[i].strip()
            
            for common_section in common_sections:
                if common_section.lower() == section_title.lower():
                    continue
                
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
            
            if i > section_start_pos + 3:
                numbered_pattern = r'^\s*\d+\.?\s+[A-Z]'
                if re.match(numbered_pattern, line_stripped):
                    word_count = len(line_stripped.split())
                    if word_count < 10:
                        section_end_pos = i
                        break
        
        # Extract section content
        section_lines = lines[section_start_pos:section_end_pos]
        section_content = '\n'.join(section_lines).strip()
        
        # Remove the header line itself if it appears at the start
        header_pattern = rf'^{re.escape(section_title)}.*?\n'
        section_content = re.sub(header_pattern, '', section_content, flags=re.IGNORECASE | re.MULTILINE)
        
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
                remaining_text = match.group(1).strip()
                if remaining_text:
                    section_lines[0] = remaining_text
                    section_content = '\n'.join(section_lines).strip()
                else:
                    if len(section_lines) > 1:
                        section_content = '\n'.join(section_lines[1:]).strip()
                break
        
        section_content = section_content.strip()
        
        return section_content
    
    def get_extraction_history(self) -> List[Dict]:
        """Get history of all extractions."""
        return self.extraction_history


def main():
    """Command-line interface for PlainTextExtractor."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract sections from a PDF file'
    )
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--paper-name', '-n', help='Name for the paper (default: derived from PDF filename)')
    parser.add_argument('--output-dir', '-o', default='extracted_sections',
                       help='Base output directory (default: extracted_sections)')
    parser.add_argument('--no-ai', action='store_true',
                       help='Disable AI-powered extraction (use rule-based)')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") if not args.no_ai else None
    
    # Extract sections
    extractor = PlainTextExtractor(output_base_dir=args.output_dir, use_ai=not args.no_ai)
    try:
        extractor.extract_all_sections(
            pdf_path=args.pdf_path,
            paper_name=args.paper_name,
            gemini_api_key=api_key
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
