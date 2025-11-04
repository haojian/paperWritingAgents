"""
Extract Sections Utility
Extracts all sections from a PDF file and saves each section as a standalone txt file
to the Extracted-sections folder. Each paper gets a subdirectory.
Files are named as 1_abstract.txt, 2_introduction.txt, etc.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict
from agents import PDFSectionExtractorAgent


class ExtractSections:
    """Utility to extract all sections from a PDF file."""
    
    def __init__(self, output_base_dir: str = "Extracted-sections"):
        """
        Initialize ExtractSections utility.
        
        Args:
            output_base_dir: Base directory for extracted sections (default: "Extracted-sections")
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
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
    
    def extract_all_sections(self, pdf_path: str, paper_name: Optional[str] = None,
                            gemini_api_key: Optional[str] = None, use_ai: bool = True):
        """
        Extract all sections from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            paper_name: Name for the paper (default: derived from PDF filename)
            gemini_api_key: Optional Gemini API key for AI-powered extraction
            use_ai: Whether to use AI for extraction (default: True)
            
        Returns:
            Dictionary mapping section numbers to extracted file paths
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Determine paper name from PDF filename if not provided
        if paper_name is None:
            paper_name = Path(pdf_path).stem
        
        # Create subdirectory for this paper
        paper_dir = self.output_base_dir / paper_name
        paper_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize extractor
        extractor = PDFSectionExtractorAgent(
            name="PDF Extractor",
            gemini_api_key=gemini_api_key,
            use_ai=use_ai
        )
        
        extracted_files = {}
        section_num = 1
        
        print(f"Extracting sections from: {pdf_path}")
        print(f"Output directory: {paper_dir}")
        print("-" * 60)
        
        # Extract each section
        for section_title in self.section_titles:
            try:
                print(f"\n[{section_num}] Extracting '{section_title}'...")
                content = extractor.extract_section(pdf_path, section_title)
                
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


def main():
    """Command-line interface for ExtractSections."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract all sections from a PDF file'
    )
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--paper-name', '-n', help='Name for the paper (default: derived from PDF filename)')
    parser.add_argument('--output-dir', '-o', default='Extracted-sections',
                       help='Base output directory (default: Extracted-sections)')
    parser.add_argument('--no-ai', action='store_true',
                       help='Disable AI-powered extraction (use rule-based)')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") if not args.no_ai else None
    
    # Extract sections
    extractor = ExtractSections(output_base_dir=args.output_dir)
    try:
        extractor.extract_all_sections(
            pdf_path=args.pdf_path,
            paper_name=args.paper_name,
            gemini_api_key=api_key,
            use_ai=not args.no_ai
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

