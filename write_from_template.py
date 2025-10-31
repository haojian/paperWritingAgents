#!/usr/bin/env python3
"""
 python write_from_template.py ideas.txt template.txt writinghistory.txt

Standalone script to generate text from ideas and template files.
Usage: python write_from_template.py <ideas_file> <template_file> <output_file> [--provider gemini|openai]
"""

import sys
import os
from agents import StudentWriterAgent


def main():
    """Main function to generate text from files."""
    
    # Parse command line arguments
    if len(sys.argv) < 4:
        print("Usage: python write_from_template.py <ideas_file> <template_file> <output_file> [--provider gemini|openai]")
        print("\nExample:")
        print('  python write_from_template.py "ideas.txt" "template.txt" "output.txt"')
        print('  python write_from_template.py "ideas.txt" "template.txt" "output.txt" --provider openai')
        print("\nRequired: Set API key for AI-powered generation")
        print('  export GEMINI_API_KEY="your_api_key_here"')
        print('  or')
        print('  export OPENAI_API_KEY="your_api_key_here"')
        sys.exit(1)
    
    ideas_file = sys.argv[1]
    template_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Check for API provider flag
    api_provider = "gemini"  # default
    if "--provider" in sys.argv:
        idx = sys.argv.index("--provider")
        if idx + 1 < len(sys.argv):
            api_provider = sys.argv[idx + 1].lower()
    
    # Check if input files exist
    if not os.path.exists(ideas_file):
        print(f"Error: Ideas file not found: {ideas_file}")
        sys.exit(1)
    
    if not os.path.exists(template_file):
        print(f"Error: Template file not found: {template_file}")
        sys.exit(1)
    
    # Get API key from environment based on provider
    if api_provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        api_key_name = "GEMINI_API_KEY"
    elif api_provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        api_key_name = "OPENAI_API_KEY"
    else:
        print(f"Error: Unknown API provider '{api_provider}'. Supported: 'gemini', 'openai'")
        sys.exit(1)
    
    if not api_key:
        print(f"Error: {api_key_name} not set. Please set it to use AI-powered generation.")
        print(f"  export {api_key_name}='your_api_key_here'")
        sys.exit(1)
    
    # Initialize writer
    print(f"Initializing Student Writer Agent ({api_provider})...")
    writer = StudentWriterAgent(
        name="Student Writer",
        api_provider=api_provider,
        gemini_api_key=api_key if api_provider == "gemini" else None,
        openai_api_key=api_key if api_provider == "openai" else None
    )
    
    # Check if API is available
    if not writer.api_available:
        print(f"Error: {api_provider.upper()} API is not available. Please check your API key.")
        sys.exit(1)
    
    print(f"\nGenerating text from:")
    print(f"  Ideas file: {ideas_file}")
    print(f"  Template file: {template_file}")
    print(f"  Output file: {output_file}")
    print("-" * 60)
    
    try:
        # Generate text and save with history
        result = writer.write_from_files(
            ideas_file_path=ideas_file,
            template_file_path=template_file,
            output_file_path=output_file
        )
        
        print("\n✓ Text generation complete!")
        print(f"  - Generated text: {len(result['generated_text'])} characters")
        print(f"  - Output saved to: {result['output_file']}")
        print(f"  - LaTeX version saved: {result.get('latex_file', 'N/A')}")
        print(f"  - Timestamp: {result['timestamp']}")
        
        # Display preview of generated text
        generated_text = result.get("generated_text", "")
        if generated_text:
            preview = generated_text[:300] + "..." if len(generated_text) > 300 else generated_text
            print(f"\nGenerated text preview:")
            print("-" * 60)
            print(preview)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    except IOError as e:
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

