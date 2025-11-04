#!/usr/bin/env python3
"""
example: python extract_section.py resources/citesee.pdf Introduction citesee-intro.txt

Standalone script to extract a section from a PDF file using AI.
Usage: python extract_section.py <pdf_path> <section_title> [output_file]

Arguments:
    pdf_path: Path to the PDF file
    section_title: Title of the section to extract (e.g., "INTRODUCTION", "Related Work")
    output_file: (Optional) Path to output text file to save the extracted content
"""

import sys
import os
from tools import PlainTextExtractor


def main():
    """Main function to extract section from PDF."""
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python extract_section.py <pdf_path> <section_title> [output_file]")
        print("\nExample:")
        print('  python extract_section.py "resources/citesee.pdf" "INTRODUCTION"')
        print('  python extract_section.py "paper.pdf" "Related Work"')
        print('  python extract_section.py "paper.pdf" "Introduction" "output.txt"')
        print("\nOptional: Set GEMINI_API_KEY environment variable for AI-powered extraction")
        print('  export GEMINI_API_KEY="your_api_key_here"')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    section_title = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Using rule-based extraction (may be less accurate).")
        print("  For better accuracy, set: export GEMINI_API_KEY='your_key_here'")
        use_ai = False
    else:
        print("✓ Using AI-powered extraction (Gemini API)")
        use_ai = True
    
    # Initialize extractor
    extractor = PlainTextExtractor(
        gemini_api_key=api_key,
        use_ai=use_ai
    )
    
    # Extract section
    print(f"\nExtracting '{section_title}' from {pdf_path}...")
    print("-" * 60)
    
    try:
        section_content = extractor.extract_section(pdf_path, section_title)
        
        print(f"\n✓ Successfully extracted '{section_title}' section!")
        print(f"  Length: {len(section_content)} characters")
        print(f"  Word Count: {len(section_content.split())} words")
        
        # Save to file if output_file is specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(section_content)
                print(f"  ✓ Saved to: {output_file}")
            except Exception as e:
                print(f"  ✗ Error saving to file: {e}", file=sys.stderr)
                return 1
        
        # Output the content
        print("\n" + "=" * 60)
        print(f"SECTION CONTENT:")
        print("=" * 60)
        print(section_content)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

