"""
Test AI-powered extraction of INTRODUCTION section from citesee.pdf
"""

from agents import PDFSectionExtractorAgent
import os

def test_citesee_ai_extraction():
    """Test extracting INTRODUCTION using AI"""
    
    print("=" * 60)
    print("TESTING AI-POWERED PDF SECTION EXTRACTION")
    print("=" * 60)
    
    # Get API key from environment or use None
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("\n⚠ No GEMINI_API_KEY found in environment.")
        print("  Set it with: export GEMINI_API_KEY='your_key_here'")
        print("  Or pass it directly: PDFSectionExtractorAgent(gemini_api_key='your_key')")
        print("\nContinuing without AI (will use rule-based extraction)...\n")
    
    # Initialize extractor with AI enabled
    extractor = PDFSectionExtractorAgent(
        name="PDF Extractor",
        gemini_api_key=api_key,
        use_ai=True
    )
    
    pdf_path = "resources/citesee.pdf"
    section_title = "INTRODUCTION"
    
    print(f"PDF File: {pdf_path}")
    print(f"Section to Extract: {section_title}")
    print(f"Using AI: {extractor.use_ai and extractor.gemini_client is not None}")
    print("\n" + "-" * 60)
    
    try:
        print("\nExtracting section...")
        section_content = extractor.extract_section(pdf_path, section_title)
        
        print(f"\n✓ Successfully extracted '{section_title}' section!")
        print(f"\nContent Statistics:")
        print(f"  Length: {len(section_content)} characters")
        print(f"  Word Count: {len(section_content.split())} words")
        print(f"  Lines: {len(section_content.split(chr(10)))}")
        
        # Show first and last parts
        print("\n" + "=" * 60)
        print("SECTION CONTENT - BEGINNING:")
        print("=" * 60)
        print(section_content[:500])
        
        print("\n" + "=" * 60)
        print("SECTION CONTENT - END:")
        print("=" * 60)
        print(section_content[-500:])
        
        # Check if it looks correct
        print("\n" + "=" * 60)
        print("VALIDATION:")
        print("=" * 60)
        if section_content.strip().startswith("Science"):
            print("✓ Content starts with 'Science' - looks like Introduction content")
        elif "Science builds on" in section_content:
            print("✓ Contains 'Science builds on' - Introduction content found")
        else:
            print("⚠ Content doesn't match expected Introduction start")
        
        # Check for next section indicators
        next_section_keywords = ["2 ", "2.", "RELATED WORK", "Related Work", "METHODOLOGY"]
        found_next = [kw for kw in next_section_keywords if kw in section_content[-200:]]
        if found_next:
            print(f"⚠ Warning: Found potential next section keywords at end: {found_next}")
            print("   This might indicate extraction includes next section")
        else:
            print("✓ No obvious next section headers found at end")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_citesee_ai_extraction()

