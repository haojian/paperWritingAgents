#!/usr/bin/env python3
"""
Test script for Style Analyzer Agent with file input/output.
Demonstrates analyzing a text file and generating a template.
"""

import os
from style_analyzer import StyleAnalyzerAgent


def main():
    """Test the analyze_file_and_generate_template method."""
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        print("Warning: GEMINI_API_KEY not set. Please set it to use AI-powered analysis.")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        return
    
    # Initialize Style Analyzer with Gemini API
    print("Initializing Style Analyzer Agent...")
    analyzer = StyleAnalyzerAgent(
        name="Style Analyzer",
        api_provider="gemini",
        gemini_api_key=gemini_api_key
    )
    
    # Check if API is available
    if not analyzer.api_available:
        print("Error: Gemini API is not available. Please check your API key.")
        return
    
    # Example: Analyze a text file and generate template
    input_file = "citesee-intro.txt"  # Path to input text file
    output_file = "template.txt"      # Path to output template file
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        print("  Please extract a section first using extract_section.py")
        return
    
    print(f"\nAnalyzing file: {input_file}")
    print(f"Generating template: {output_file}")
    print("-" * 60)
    
    try:
        # Analyze file and generate template
        result = analyzer.analyze_file_and_generate_template(
            input_file_path=input_file,
            output_file_path=output_file,
            section_name="Introduction"  # Optional: will infer from filename if not provided
        )
        
        print("\n✓ Analysis complete!")
        print(f"  - Analyzed {len(result['sentences'])} sentences")
        print(f"  - Found {len(result['transitions'])} transitions")
        print(f"  - Template saved to: {result['output_file']}")
        
        # Display template preview
        template = result.get("template", "")
        if template:
            preview = template[:200] + "..." if len(template) > 200 else template
            print(f"\nTemplate preview:")
            print(f"  {preview}")
        
        # Show a few sentence analyses
        if result.get("sentences"):
            print("\nSample sentence analyses:")
            for i, sentence_analysis in enumerate(result["sentences"][:3]):
                print(f"\n  Sentence {sentence_analysis.get('sentence_index', i) + 1}:")
                print(f"    Text: {sentence_analysis.get('text', '')[:80]}...")
                print(f"    Role: {sentence_analysis.get('role', 'unknown')}")
                if sentence_analysis.get('transition_type'):
                    print(f"    Transition: {sentence_analysis.get('transition_type')}")
        
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

