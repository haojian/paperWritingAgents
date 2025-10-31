#!/usr/bin/env python3
"""
Standalone script to generate professor feedback as actionable to-do list.
Usage: python generate_feedback.py <heuristics_file> <writinghistory_file> <output_file> [--provider gemini|openai]
"""

import sys
import os
from agents import ProfessorFeedbackAgent


def main():
    """Main function to generate feedback from files."""
    
    # Parse command line arguments
    if len(sys.argv) < 4:
        print("Usage: python generate_feedback.py <heuristics_file> <writinghistory_file> <output_file> [--provider gemini|openai]")
        print("\nExample:")
        print('  python generate_feedback.py "heuristics.txt" "writinghistory.txt" "todo_list.txt"')
        print('  python generate_feedback.py "heuristics.txt" "writinghistory.txt" "todo_list.txt" --provider openai')
        print("\nRequired: Set API key for AI-powered feedback generation")
        print('  export GEMINI_API_KEY="your_api_key_here"')
        print('  or')
        print('  export OPENAI_API_KEY="your_api_key_here"')
        sys.exit(1)
    
    heuristics_file = sys.argv[1]
    writinghistory_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Check for API provider flag
    api_provider = "gemini"  # default
    if "--provider" in sys.argv:
        idx = sys.argv.index("--provider")
        if idx + 1 < len(sys.argv):
            api_provider = sys.argv[idx + 1].lower()
    
    # Check if input files exist
    if not os.path.exists(heuristics_file):
        print(f"Error: Heuristics file not found: {heuristics_file}")
        sys.exit(1)
    
    if not os.path.exists(writinghistory_file):
        print(f"Error: Writing history file not found: {writinghistory_file}")
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
        print(f"Error: {api_key_name} not set. Please set it to use AI-powered feedback generation.")
        print(f"  export {api_key_name}='your_api_key_here'")
        sys.exit(1)
    
    # Initialize professor agent
    print(f"Initializing Professor Feedback Agent ({api_provider})...")
    professor = ProfessorFeedbackAgent(
        name="Professor Feedback",
        expertise="Academic Writing",
        api_provider=api_provider,
        gemini_api_key=api_key if api_provider == "gemini" else None,
        openai_api_key=api_key if api_provider == "openai" else None
    )
    
    # Check if API is available
    if not professor.api_available:
        print(f"Error: {api_provider.upper()} API is not available. Please check your API key.")
        sys.exit(1)
    
    print(f"\nGenerating feedback:")
    print(f"  Heuristics file: {heuristics_file}")
    print(f"  Writing history: {writinghistory_file}")
    print(f"  Output file: {output_file}")
    print("-" * 60)
    
    try:
        # Generate feedback
        result = professor.generate_feedback_from_files(
            heuristics_file_path=heuristics_file,
            writinghistory_file_path=writinghistory_file,
            output_file_path=output_file
        )
        
        print("\n✓ Feedback generation complete!")
        print(f"  - To-do list saved to: {result['output_file']}")
        print(f"  - Latest writing length: {len(result['latest_writing'])} characters")
        print(f"  - To-do list history maintained (latest at top)")
        
        # Show history info
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                todo_count = content.count("TODO LIST #")
                print(f"  - Total to-do lists in history: {todo_count}")
        
        # Display preview of to-do list
        todo_list = result.get("todo_list", "")
        if todo_list:
            preview = todo_list[:400] + "..." if len(todo_list) > 400 else todo_list
            print(f"\nTo-do list preview:")
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

