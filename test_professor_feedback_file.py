#!/usr/bin/env python3
"""
Test script for Professor Feedback Agent with file input/output.
Demonstrates generating actionable to-do list from heuristics and writing history.
"""

import os
from agents import ProfessorFeedbackAgent


def main():
    """Test the generate_feedback_from_files method."""
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        print("Warning: GEMINI_API_KEY not set. Please set it to use AI-powered feedback generation.")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        return
    
    # Initialize Professor with Gemini API
    print("Initializing Professor Feedback Agent...")
    professor = ProfessorFeedbackAgent(
        name="Professor Feedback",
        expertise="Academic Writing",
        api_provider="gemini",
        gemini_api_key=gemini_api_key
    )
    
    # Check if API is available
    if not professor.api_available:
        print("Error: Gemini API is not available. Please check your API key.")
        return
    
    # Example files
    heuristics_file = "heuristics.txt"  # Path to heuristics file
    writinghistory_file = "writinghistory.txt"  # Path to writing history
    output_file = "todo_list.txt"  # Path to output to-do list
    
    # Check if input files exist
    if not os.path.exists(heuristics_file):
        print(f"Error: Heuristics file not found: {heuristics_file}")
        print("  Create a file with evaluation heuristics first")
        return
    
    if not os.path.exists(writinghistory_file):
        print(f"Error: Writing history file not found: {writinghistory_file}")
        print("  Generate writing history first using write_from_template.py")
        return
    
    print(f"\nGenerating feedback from:")
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
        print(f"  - Latest writing extracted: {len(result['latest_writing'])} characters")
        
        # Display preview
        todo_list = result.get("todo_list", "")
        if todo_list:
            preview = todo_list[:400] + "..." if len(todo_list) > 400 else todo_list
            print(f"\nTo-do list preview:")
            print("-" * 60)
            print(preview)
        
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

