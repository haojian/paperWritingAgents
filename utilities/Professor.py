"""
Professor Utility
Loads data from global_memory.txt and creates a set of to-do items.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict
from professor_feedback import ProfessorFeedbackAgent


class Professor:
    """Utility to generate to-do items from global memory."""
    
    def __init__(self, global_memory_file: str = "global_memory.txt",
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Professor utility.
        
        Args:
            global_memory_file: Path to global memory file (default: "global_memory.txt")
            api_provider: "gemini" or "openai" (default: "gemini")
            gemini_api_key: Optional Gemini API key
            openai_api_key: Optional OpenAI API key
        """
        self.global_memory_file = Path(global_memory_file)
        self.professor = ProfessorFeedbackAgent(
            name="Professor",
            expertise="Academic Writing",
            api_provider=api_provider,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key
        )
    
    def load_global_memory(self) -> str:
        """
        Load global memory from file.
        
        Returns:
            Global memory content as string
        """
        if not self.global_memory_file.exists():
            # Create default global memory file
            with open(self.global_memory_file, 'w', encoding='utf-8') as f:
                f.write("===== Writing Heuristics =====\n\n")
                f.write("• Clarity: Ensure ideas are clearly expressed\n")
                f.write("• Structure: Follow logical flow\n")
                f.write("• Academic Tone: Maintain formal academic style\n")
                f.write("• Evidence: Support claims with evidence\n")
                f.write("• Coherence: Ensure smooth transitions\n\n")
            print(f"Created default {self.global_memory_file}")
        
        with open(self.global_memory_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def generate_todo_list(self, writing_history_file: str, 
                          output_file: Optional[str] = None) -> str:
        """
        Generate to-do list from writing history using global memory as heuristics.
        
        Args:
            writing_history_file: Path to writing history file
            output_file: Optional output file path (default: creates todo_list.txt)
            
        Returns:
            Generated to-do list as string
        """
        # Load global memory (heuristics)
        heuristics = self.load_global_memory()
        
        # Create temporary heuristics file if needed
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(heuristics)
            temp_heuristics_file = f.name
        
        try:
            # Determine output file
            if output_file is None:
                output_file = Path(writing_history_file).parent / "TodoHistory.txt"
            else:
                output_file = Path(output_file)
            
            # Generate feedback
            result = self.professor.generate_feedback_from_files(
                heuristics_file_path=temp_heuristics_file,
                writinghistory_file_path=writing_history_file,
                output_file_path=str(output_file)
            )
            
            return result.get('todo_list', '')
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_heuristics_file):
                os.unlink(temp_heuristics_file)
    
    def review_writing(self, writing_content: str, topic: str = "") -> Dict:
        """
        Review writing content and provide feedback.
        
        Args:
            writing_content: Writing content to review
            topic: Optional topic/context
            
        Returns:
            Review feedback dictionary
        """
        # Load heuristics from global memory
        heuristics = self.load_global_memory()
        
        # Create a simple paper structure for review
        paper = {"Content": writing_content}
        
        # Get feedback
        feedback = self.professor.review_paper(paper, topic)
        
        return feedback


def main():
    """Command-line interface for Professor."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate to-do list from writing history using global memory'
    )
    parser.add_argument('writing_history', help='Path to writing history file')
    parser.add_argument('--output', '-o', help='Output file path (default: TodoHistory.txt in same directory)')
    parser.add_argument('--global-memory', '-g', default='global_memory.txt',
                       help='Path to global memory file (default: global_memory.txt)')
    parser.add_argument('--provider', default='gemini', choices=['gemini', 'openai'],
                       help='API provider (default: gemini)')
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_key = os.getenv("GEMINI_API_KEY") if args.provider == "gemini" else None
    openai_key = os.getenv("OPENAI_API_KEY") if args.provider == "openai" else None
    
    professor = Professor(
        global_memory_file=args.global_memory,
        api_provider=args.provider,
        gemini_api_key=gemini_key,
        openai_api_key=openai_key
    )
    
    try:
        todo_list = professor.generate_todo_list(
            writing_history_file=args.writing_history,
            output_file=args.output
        )
        print("✓ To-do list generated successfully!")
        if todo_list:
            print("\nTo-do list preview:")
            print(todo_list[:500] + "..." if len(todo_list) > 500 else todo_list)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

