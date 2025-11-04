"""
Writer
Manual mode: Takes input from different memory files.
Can ask professor to review and get a todo list to improve.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from .MemoryManager import MemoryManager
from tools.CloudAIWrapper import CloudAIWrapper
from tools.Professor import Professor
from student_writer import StudentWriterAgent


class Writer:
    """Writer for paragraph-writing mode."""
    
    def __init__(self, project_path: str,
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Writer.
        
        Args:
            project_path: Path to project directory
            api_provider: "gemini" or "openai" (default: "gemini")
            gemini_api_key: Optional Gemini API key
            openai_api_key: Optional OpenAI API key
        """
        self.project_path = Path(project_path)
        self.memory_manager = MemoryManager()
        self.ai_wrapper = CloudAIWrapper(
            provider=api_provider,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key
        )
        self.professor = Professor(
            api_provider=api_provider,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key
        )
        self.writer_agent = StudentWriterAgent(
            name="Writer",
            api_provider=api_provider,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key
        )
        
        # Project file paths
        self.project_memory_file = self.project_path / "Project Memory" / "ProjectMemory.txt"
        self.temp_memory_file = self.project_path / "Project Memory" / "TempMemory.txt"
        self.writing_history_file = self.project_path / "Intermediate" / "AutoWritingHistory.txt"
        self.todo_history_file = self.project_path / "Intermediate" / "TodoHistory.txt"
        self.output_plaintext = self.project_path / "Output" / "plaintext.txt"
        self.output_file = self.project_path / "Output" / "output.txt"
    
    def write_paragraph(self, paragraph_template: Optional[str] = None) -> str:
        """
        Write a paragraph using project memory and optional template.
        
        Args:
            paragraph_template: Optional paragraph template
            
        Returns:
            Generated paragraph text
        """
        # Load all memory
        project_memory = self.memory_manager.load_project_memory(str(self.project_memory_file))
        temp_memory = self.memory_manager.load_temp_memory(str(self.temp_memory_file))
        
        # Get key ideas
        key_ideas = project_memory.get("Key Ideas", [])
        ideas_text = "\n".join(f"• {idea}" for idea in key_ideas)
        
        # Get revision feedback
        revision_feedback = temp_memory.get("Revision Feedback", [])
        feedback_text = "\n".join(f"• {fb}" for fb in revision_feedback) if revision_feedback else ""
        
        # Create prompt
        prompt = f"""Write a research paper paragraph based on the following information:

===== Key Ideas =====
{ideas_text}

"""
        
        if paragraph_template:
            prompt += f"""===== Paragraph Template =====
{paragraph_template}

"""
        
        if feedback_text:
            prompt += f"""===== Revision Feedback =====
{feedback_text}

Please address the feedback in your writing.
"""
        
        prompt += """
Write a well-structured, academic paragraph that:
- Clearly expresses the key ideas
- Follows the template structure (if provided)
- Addresses any revision feedback
- Maintains academic tone and style
"""
        
        # Generate text
        generated_text = self.ai_wrapper.generate(prompt)
        
        # Save to writing history
        self._append_to_history(generated_text)
        
        # Save to output files
        self._save_output(generated_text)
        
        return generated_text
    
    def ask_professor_review(self) -> str:
        """
        Ask professor to review current writing and generate todo list.
        
        Returns:
            Generated todo list
        """
        # Load writing history
        if not self.writing_history_file.exists():
            raise ValueError(f"Writing history file not found: {self.writing_history_file}")
        
        # Generate todo list
        todo_list = self.professor.generate_todo_list(
            writing_history_file=str(self.writing_history_file),
            output_file=str(self.todo_history_file)
        )
        
        return todo_list
    
    def revise_from_todo(self, paragraph_template: Optional[str] = None) -> str:
        """
        Revise writing based on todo list.
        
        Args:
            paragraph_template: Optional paragraph template
            
        Returns:
            Revised paragraph text
        """
        # Load todo history
        if not self.todo_history_file.exists():
            raise ValueError(f"Todo history file not found: {self.todo_history_file}")
        
        # Revise using writer agent
        result = self.writer_agent.revise_from_todo_list(
            todo_list_file_path=str(self.todo_history_file),
            writinghistory_file_path=str(self.writing_history_file),
            ideas_file_path=str(self.project_memory_file) if self.project_memory_file.exists() else None,
            template_file_path=None  # Could add template file support
        )
        
        revised_text = result.get('revised_text', '')
        
        # Save to output
        self._save_output(revised_text)
        
        return revised_text
    
    def _append_to_history(self, text: str):
        """Append text to writing history."""
        with open(self.writing_history_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"REVISION #{len(self._read_history_entries()) + 1}\n")
            f.write(f"{'='*80}\n\n")
            f.write(text)
            f.write("\n\n")
    
    def _read_history_entries(self) -> List[str]:
        """Read all history entries."""
        if not self.writing_history_file.exists():
            return []
        
        with open(self.writing_history_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple parsing - count REVISION markers
            return content.split('REVISION #')
    
    def _save_output(self, text: str):
        """Save text to output files."""
        # Save to plaintext.txt (latest at top)
        with open(self.output_plaintext, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Save to output.txt (append)
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(text)
            f.write("\n")


def main():
    """Command-line interface for Writer."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Write paragraphs using project memory'
    )
    parser.add_argument('project_path', help='Path to project directory')
    parser.add_argument('--template', '-t', help='Paragraph template file')
    parser.add_argument('--review', action='store_true', help='Ask professor for review')
    parser.add_argument('--revise', action='store_true', help='Revise based on todo list')
    parser.add_argument('--provider', default='gemini', choices=['gemini', 'openai'],
                       help='API provider (default: gemini)')
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_key = os.getenv("GEMINI_API_KEY") if args.provider == "gemini" else None
    openai_key = os.getenv("OPENAI_API_KEY") if args.provider == "openai" else None
    
    writer = Writer(
        project_path=args.project_path,
        api_provider=args.provider,
        gemini_api_key=gemini_key,
        openai_api_key=openai_key
    )
    
    try:
        if args.review:
            todo_list = writer.ask_professor_review()
            print("✓ Review complete! Todo list generated.")
            print("\nTodo list:")
            print(todo_list)
        elif args.revise:
            revised = writer.revise_from_todo()
            print("✓ Revision complete!")
            print("\nRevised text:")
            print(revised)
        else:
            # Load template if provided
            template = None
            if args.template:
                with open(args.template, 'r') as f:
                    template = f.read()
            
            paragraph = writer.write_paragraph(paragraph_template=template)
            print("✓ Paragraph written!")
            print("\nGenerated paragraph:")
            print(paragraph)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

