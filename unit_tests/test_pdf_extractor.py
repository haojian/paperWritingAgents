"""
Test script for PDF Section Extractor Agent
Tests PDF reading and single section extraction.
"""

from tools import PlainTextExtractor
import os

def test_pdf_extractor():
    """Test the PDF section extractor with a sample PDF."""
    
    # Initialize extractor
    extractor = PlainTextExtractor()
    
    print("=" * 60)
    print("PDF SECTION EXTRACTOR TEST")
    print("=" * 60)
    
    print("\nUsage:")
    print('  content = extractor.extract_section("path/to/paper.pdf", "Introduction")')
    print('  # Returns the content of the Introduction section as a string')
    
    # Example usage
    example_code = '''
# Example: Extract a specific section
pdf_path = "sample_paper.pdf"
section_title = "Introduction"

extractor = PlainTextExtractor()
section_content = extractor.extract_section(pdf_path, section_title)

print(f"\\nExtracted '{section_title}' section:")
print(f"  Length: {len(section_content)} characters")
print(f"  Preview: {section_content[:300]}...")

# Extract multiple sections
sections_to_extract = ["Introduction", "Related Work", "Methodology", "Results"]

for section_title in sections_to_extract:
    try:
        content = extractor.extract_section(pdf_path, section_title)
        print(f"\\n{section_title}:")
        print(f"  Length: {len(content)} characters")
    except ValueError as e:
        print(f"\\n{section_title}: Not found - {e}")
'''
    
    print("\n\nExample Code:")
    print("-" * 60)
    print(example_code)
    
    print("\n" + "=" * 60)
    print("Note: To test with an actual PDF:")
    print("  1. Place a PDF file in the project directory")
    print("  2. Update pdf_path in the example code")
    print("  3. Run the script")
    print("=" * 60)
    
    # Test with a non-existent file to show error handling
    print("\n\nTesting Error Handling:")
    print("-" * 60)
    try:
        extractor.extract_section("nonexistent.pdf", "Introduction")
    except FileNotFoundError as e:
        print(f"✓ Correctly caught FileNotFoundError: {e}")
    
    # Test with non-existent section
    print("\nNote: If a section is not found, ValueError will be raised")
    print("  Example: extractor.extract_section('paper.pdf', 'NonExistentSection')")
    print("  Will raise: ValueError: Section 'NonExistentSection' not found in PDF")
    
    # Check PDF libraries availability
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
    
    if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
            print("\n⚠ Warning: No PDF parsing library installed.")
            print("  Install with: pip install pdfplumber  (recommended)")
            print("  Or: pip install PyPDF2")

if __name__ == "__main__":
    test_pdf_extractor()
