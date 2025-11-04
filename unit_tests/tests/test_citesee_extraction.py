"""
Test extraction of INTRODUCTION section from citesee.pdf
"""

from tools import PlainTextExtractor
import os

def test_citesee_extraction():
    """Test extracting INTRODUCTION from citesee.pdf"""
    
    print("=" * 60)
    print("TESTING PDF SECTION EXTRACTION")
    print("=" * 60)
    
    # Initialize extractor with AI support
    # Set GEMINI_API_KEY environment variable for AI-powered extraction
    api_key = os.getenv("GEMINI_API_KEY")
    extractor = PlainTextExtractor(
        gemini_api_key=api_key,
        use_ai=True  # Enable AI-powered extraction
    )
    
    pdf_path = "resources/citesee.pdf"
    section_title = "INTRODUCTION"
    
    print(f"\nPDF File: {pdf_path}")
    print(f"Section to Extract: {section_title}")
    print("\n" + "-" * 60)
    
    try:
        # Extract the Introduction section
        print("\nExtracting section...")
        section_content = extractor.extract_section(pdf_path, section_title)
        
        print(f"\n✓ Successfully extracted '{section_title}' section!")
        print(f"\nContent Length: {len(section_content)} characters")
        print(f"Word Count: {len(section_content.split())} words")
        
        # Show preview
        print("\n" + "=" * 60)
        print("SECTION CONTENT PREVIEW:")
        print("=" * 60)
        print(section_content[:1000] + "..." if len(section_content) > 1000 else section_content)
        
        # Show full content length info
        if len(section_content) > 1000:
            print(f"\n... (showing first 1000 characters of {len(section_content)} total)")
        
        # Show extraction history
        print("\n" + "-" * 60)
        print("EXTRACTION HISTORY:")
        print("-" * 60)
        for entry in extractor.get_extraction_history():
            print(f"  PDF: {entry['pdf_path']}")
            print(f"  Section: {entry['section_title']}")
            print(f"  Content Length: {entry['content_length']} characters")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nTrying alternative section title variations...")
        
        # Try different variations
        variations = ["Introduction", "INTRODUCTION", "1. Introduction", "1 INTRODUCTION"]
        for variation in variations:
            try:
                print(f"\nTrying: '{variation}'...")
                content = extractor.extract_section(pdf_path, variation)
                print(f"✓ Found section with title: '{variation}'")
                print(f"  Length: {len(content)} characters")
                print(f"  Preview: {content[:300]}...")
                break
            except ValueError:
                print(f"  Not found as '{variation}'")
                continue
        else:
            print("\n✗ Could not find Introduction section with any variation")
            
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_citesee_extraction()

