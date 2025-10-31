"""
Debug script to see what's in the PDF
"""

from agents import PDFSectionExtractorAgent

def debug_pdf():
    """Debug the PDF to see its structure"""
    
    extractor = PDFSectionExtractorAgent()
    pdf_path = "resources/citesee.pdf"
    
    print("=" * 60)
    print("DEBUGGING PDF STRUCTURE")
    print("=" * 60)
    
    try:
        # Try to extract text
        text = extractor._extract_text_from_pdf(pdf_path)
        
        print(f"\nTotal text length: {len(text)} characters")
        print(f"Total lines: {len(text.split(chr(10)))}")
        
        # Show first 2000 characters to see structure
        print("\n" + "=" * 60)
        print("FIRST 2000 CHARACTERS OF PDF:")
        print("=" * 60)
        print(text[:2000])
        
        # Look for section headers
        print("\n" + "=" * 60)
        print("LOOKING FOR SECTION HEADERS:")
        print("=" * 60)
        
        lines = text.split('\n')
        for i, line in enumerate(lines[:100]):  # Check first 100 lines
            line_stripped = line.strip()
            # Look for lines that might be headers
            if line_stripped and (
                'introduction' in line_stripped.lower() or
                'abstract' in line_stripped.lower() or
                'related' in line_stripped.lower() or
                line_stripped.isupper() and len(line_stripped.split()) < 5 or
                re.match(r'^\d+\.?\s+[A-Z]', line_stripped)
            ):
                print(f"Line {i}: {repr(line_stripped)}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import re
    debug_pdf()

