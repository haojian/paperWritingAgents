#!/usr/bin/env python3
"""
   python revise_from_todo.py "todo_list.txt" "writinghistory.txt" "ideas.txt" "template.txt"


Standalone script to revise writing based on todo list.
Usage: python revise_from_todo.py <todo_list_file> <writinghistory_file> [ideas_file] [template_file] [--provider gemini|openai]
"""

import sys
import os
from agents import StudentWriterAgent


def main():
    """Main function to revise writing from todo list."""
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python revise_from_todo.py <todo_list_file> <writinghistory_file> [ideas_file] [template_file] [--provider gemini|openai]")
        print("\nExample:")
        print('  python revise_from_todo.py "todo_list.txt" "writinghistory.txt"')
        print('  python revise_from_todo.py "todo_list.txt" "writinghistory.txt" "ideas.txt" "template.txt"')
        print('  python revise_from_todo.py "todo_list.txt" "writinghistory.txt" --provider openai')
        print("\nRequired: Set API key for AI-powered revision")
        print('  export GEMINI_API_KEY="your_api_key_here"')
        print('  or')
        print('  export OPENAI_API_KEY="your_api_key_here"')
        sys.exit(1)
    
    todo_list_file = sys.argv[1]
    writinghistory_file = sys.argv[2]
    
    # Optional arguments
    ideas_file = None
    template_file = None
    api_provider = "gemini"  # default
    
    # Parse remaining arguments
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--provider" and i + 1 < len(sys.argv):
            api_provider = sys.argv[i + 1].lower()
            i += 2
        elif ideas_file is None and not sys.argv[i].startswith("--"):
            ideas_file = sys.argv[i]
            i += 1
        elif template_file is None and not sys.argv[i].startswith("--"):
            template_file = sys.argv[i]
            i += 1
        else:
            i += 1
    
    # Check if input files exist
    if not os.path.exists(todo_list_file):
        print(f"Error: Todo list file not found: {todo_list_file}")
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
        print(f"Error: {api_key_name} not set. Please set it to use AI-powered revision.")
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
    
    print(f"\nRevising writing:")
    print(f"  Todo list: {todo_list_file}")
    print(f"  Writing history: {writinghistory_file}")
    if ideas_file:
        print(f"  Ideas file: {ideas_file}")
    if template_file:
        print(f"  Template file: {template_file}")
    print("-" * 60)
    
    # Check if todo list file contains history and show info
    try:
        with open(todo_list_file, 'r', encoding='utf-8') as f:
            todo_preview = f.read(200)
        if "TODO LIST #" in todo_preview:
            print(f"  Note: Todo list file contains history. Only the latest to-do list will be used.")
    except:
        pass
    
    try:
        # Revise based on todo list
        result = writer.revise_from_todo_list(
            todo_list_file_path=todo_list_file,
            writinghistory_file_path=writinghistory_file,
            ideas_file_path=ideas_file,
            template_file_path=template_file
        )
        
        print("\n✓ Revision complete!")
        print(f"  - Revised text length: {len(result['revised_text'])} characters")
        print(f"  - Original text length: {len(result['original_writing'])} characters")
        print(f"  - Writing history updated: {result['output_file']}")
        print(f"  - LaTeX version saved: {result.get('latex_file', 'N/A')}")
        print(f"  - Timestamp: {result['timestamp']}")
        
        # Display preview of revised text
        revised_text = result.get("revised_text", "")
        if revised_text:
            preview = revised_text[:400] + "..." if len(revised_text) > 400 else revised_text
            print(f"\nRevised text preview:")
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

