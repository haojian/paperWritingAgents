#!/usr/bin/env python3
"""
Standalone script to analyze a text file and generate a template.
Usage: python analyze_and_generate_template.py <input_file> <output_file> [section_name]
"""

import sys
import os
from agents import StyleAnalyzerAgent


def main():
    """Main function to analyze file and generate template."""
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python analyze_and_generate_template.py <input_file> <output_file> [section_name]")
        print("\nExample:")
        print('  python analyze_and_generate_template.py "citesee-intro.txt" "template.txt"')
        print('  python analyze_and_generate_template.py "intro.txt" "template.txt" "Introduction"')
        print("\nOptional: Set GEMINI_API_KEY environment variable for AI-powered analysis")
        print('  export GEMINI_API_KEY="your_api_key_here"')
        print("\nAlternatively, set OPENAI_API_KEY for OpenAI:")
        print('  export OPENAI_API_KEY="your_api_key_here"')
        print('  python analyze_and_generate_template.py "intro.txt" "template.txt" --provider openai')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    section_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Check for API provider flag
    api_provider = "gemini"  # default
    if "--provider" in sys.argv:
        idx = sys.argv.index("--provider")
        if idx + 1 < len(sys.argv):
            api_provider = sys.argv[idx + 1].lower()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
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
        print(f"Warning: {api_key_name} not set. Please set it to use AI-powered analysis.")
        print(f"  export {api_key_name}='your_api_key_here'")
        sys.exit(1)
    
    # Initialize analyzer
    print(f"Initializing Style Analyzer Agent ({api_provider})...")
    analyzer = StyleAnalyzerAgent(
        name="Style Analyzer",
        api_provider=api_provider,
        gemini_api_key=api_key if api_provider == "gemini" else None,
        openai_api_key=api_key if api_provider == "openai" else None
    )
    
    # Check if API is available
    if not analyzer.api_available:
        print(f"Error: {api_provider.upper()} API is not available. Please check your API key.")
        sys.exit(1)
    
    print(f"\nAnalyzing file: {input_file}")
    print(f"Generating template: {output_file}")
    if section_name:
        print(f"Section name: {section_name}")
    print("-" * 60)
    
    try:
        # Analyze file and generate template
        result = analyzer.analyze_file_and_generate_template(
            input_file_path=input_file,
            output_file_path=output_file,
            section_name=section_name
        )
        
        print("\n✓ Analysis complete!")
        print(f"  - Analyzed {len(result['sentences'])} sentences")
        print(f"  - Found {len(result['transitions'])} transitions")
        print(f"  - Template saved to: {result['output_file']}")
        
        # Display template preview
        template = result.get("template", "")
        if template:
            print(f"\nTemplate ({len(template)} characters):")
            print("-" * 60)
            # Show first 500 characters
            preview = template[:500] + "..." if len(template) > 500 else template
            print(preview)
        
        # Show first few sentence analyses
        if result.get("sentences"):
            print(f"\n\nSample sentence analyses (showing first 3 of {len(result['sentences'])}):")
            print("-" * 60)
            for i, sentence_analysis in enumerate(result["sentences"][:3]):
                print(f"\n  Sentence {sentence_analysis.get('sentence_index', i) + 1}:")
                text = sentence_analysis.get('text', '')
                print(f"    Text: {text[:100]}..." if len(text) > 100 else f"    Text: {text}")
                print(f"    Role: {sentence_analysis.get('role', 'unknown')}")
                if sentence_analysis.get('transition_type'):
                    print(f"    Transition: {sentence_analysis.get('transition_type')}")
        
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

