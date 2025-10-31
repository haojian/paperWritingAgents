#!/usr/bin/env python3
"""
Test script for Student Writer Agent with file input/output.
Demonstrates generating text from ideas and template files.
"""

import os
from agents import StudentWriterAgent


def main():
    """Test the write_from_files method."""
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        print("Warning: GEMINI_API_KEY not set. Please set it to use AI-powered generation.")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        return
    
    # Initialize Student Writer with Gemini API
    print("Initializing Student Writer Agent...")
    writer = StudentWriterAgent(
        name="Student Writer",
        api_provider="gemini",
        gemini_api_key=gemini_api_key
    )
    
    # Check if API is available
    if not writer.api_available:
        print("Error: Gemini API is not available. Please check your API key.")
        return
    
    # Example files
    ideas_file = "ideas.txt"  # Path to ideas file
    template_file = "template.txt"  # Path to template file
    output_file = "writing_history.txt"  # Path to output file with history
    
    # Check if input files exist
    if not os.path.exists(ideas_file):
        print(f"Error: Ideas file not found: {ideas_file}")
        print("  Create a file with your main ideas first")
        return
    
    if not os.path.exists(template_file):
        print(f"Error: Template file not found: {template_file}")
        print("  Generate a template first using analyze_and_generate_template.py")
        return
    
    print(f"\nGenerating text from:")
    print(f"  Ideas file: {ideas_file}")
    print(f"  Template file: {template_file}")
    print(f"  Output file: {output_file}")
    print("-" * 60)
    
    try:
        # Generate text from files
        result = writer.write_from_files(
            ideas_file_path=ideas_file,
            template_file_path=template_file,
            output_file_path=output_file
        )
        
        print("\n✓ Generation complete!")
        print(f"  - Generated text: {len(result['generated_text'])} characters")
        print(f"  - Saved to: {result['output_file']}")
        print(f"  - Timestamp: {result['timestamp']}")
        
        # Display preview
        generated_text = result.get("generated_text", "")
        if generated_text:
            preview = generated_text[:300] + "..." if len(generated_text) > 300 else generated_text
            print(f"\nGenerated text preview:")
            print("-" * 60)
            print(preview)
        
        # Show that history is maintained
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                revisions = content.count("REVISION #")
                print(f"\n  - Total revisions in history: {revisions}")
                print(f"  - Latest revision is at the top of the file")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except IOError as e:
        print(f"\n✗ Error: {e}")
    except ValueError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

