"""
Writer
Supports multiple writing modes for research paper writing.
Uses tools from the tools folder and loads memories from the project folder.

Usage:
    # Command-line interface
    python -m agents.Writer MyProject --mode newparagraph
    python -m agents.Writer MyProject --mode reviseparagraph
    
    # Programmatic usage
    from agents import Writer
    
    writer = Writer(project_path="MyProject")
    # Note: project_path is relative to the projects/ directory
    
    # NewParagraph mode: Write a new paragraph
    # Requires TempMemory.txt with: Topic Sentence, Bullet Points, Template Flow (optional)
    # Any content in "Current Paragraph" is ignored for this mode.
    result = writer.new_paragraph()
    # Returns: {'plain_text': ..., 'latex': ...}
    
    #     ReviseParagraph mode: Revise an existing paragraph
    # Requires TempMemory.txt with: Current Paragraph, Revision Feedback (or inline comments in {})
    # Optional: Topic Sentence, Bullet Points, Template Flow
    result = writer.revise_paragraph()
    # Returns: {'plain_text': ..., 'latex': ..., 'version': 1}
    # Saves to WritingHistory.txt with version number
    
    # Inline Comments Feature:
    # You can add inline comments in curly braces {} within your text.
    # Example: "This is a sentence. {Improve this sentence to be more concise.}"
    # The writer will extract these comments and use them as revision feedback.
    # Comments are automatically removed from the final output.
    
Memory Files:
    ProjectMemory.txt (in Memory/ folder):
        - Key Ideas: Key ideas for the paper
        - Previous Content: Previous content from the paper
    
    TempMemory.txt (in Memory/ folder):
        - Writing Context: The task/context for writing (at the top)
        - Topic Sentence: Topic sentence for the paragraph
        - Bullet Points: Bullet points to expand on
        - Template Flow: Template describing the logic flow
        - Current Paragraph: Current paragraph content (for revision)
          * Can include inline comments in curly braces: {comment text}
          * Example: "This sentence needs work. {Make it more concise.}"
        - Revision Feedback: Feedback on what needs to be changed (for revision)
        - Output: The resulting paragraph (at the bottom, written by the writer)

Output Files:
    - WritingHistory.txt: Plain text history of all writing (with version numbers for revisions)
    - Output/Latex.txt: Latest LaTeX formatted output
    - Output/Plaintext.txt: Latest plain text output
    - Intermediate/prompt.txt: Log of the exact prompts sent to the AI (per mode run)
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

# Handle imports when run as script or module
try:
    from tools.MemoryManager import MemoryManager
except ImportError:
    # Add parent directory to path when run as script
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.MemoryManager import MemoryManager

from tools.CloudAIWrapper import CloudAIWrapper
from tools.Professor import Professor


class Writer:
    """Writer with multiple modes for research paper writing."""
    
    def __init__(self, project_path: str,
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Writer.
        
        Args:
            project_path: Project name or path relative to projects/ directory (e.g., "MyProject")
                         If it doesn't start with "projects/", it will be automatically prepended.
            api_provider: "gemini" or "openai" (default: "gemini")
            gemini_api_key: Optional Gemini API key
            openai_api_key: Optional OpenAI API key
        """
        # Automatically prepend "projects/" if not already present
        if not project_path.startswith("projects/"):
            project_path = f"projects/{project_path}"
        
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
        
        # Project file paths (updated to match new structure)
        self.project_memory_file = self.project_path / "Memory" / "ProjectMemory.txt"
        self.temp_memory_file = self.project_path / "Memory" / "TempMemory.txt"
        self.writing_history_file = self.project_path / "Intermediate" / "WritingHistory.txt"
        self.todo_history_file = self.project_path / "Intermediate" / "TodoHistory.txt"
        self.prompt_history_file = self.project_path / "Intermediate" / "prompt.txt"
        self.output_plaintext = self.project_path / "Output" / "Plaintext.txt"
        self.output_latex = self.project_path / "Output" / "Latex.txt"
        # Legacy: kept for backward compatibility but not used in new modes
        self.output_file = self.project_path / "Output" / "output.txt"
    
    def new_paragraph(self) -> Dict[str, str]:
        """
        NewParagraph mode: Write a new paragraph based on input from TempMemory.txt.
        
        Reads from TempMemory.txt which contains:
        - Writing Context: The task/context for writing
        - Topic Sentence: The topic sentence for the paragraph
        - Bullet Points: Bullet points to expand on
        - Template Flow: Template describing the logic flow (optional)
        
        Outputs:
        - Plain text to WritingHistory.txt
        - LaTeX to Output/Latex.txt
        - Resulting paragraph to TempMemory.txt Output section
        
        Returns:
            Dictionary with 'plain_text' and 'latex' keys containing the generated text
        """
        # Load memory from TempMemory.txt
        temp_memory = self.memory_manager.load_temp_memory(str(self.temp_memory_file))
        
        # Load project memory for context
        project_memory = self.memory_manager.load_project_memory(str(self.project_memory_file))
        
        # Extract components from TempMemory
        writing_context_items = temp_memory.get("Writing Context", [])
        writing_context = "\n".join(writing_context_items) if writing_context_items else None
        
        topic_sentence_items = temp_memory.get("Topic Sentence", [])
        topic_sentence = topic_sentence_items[0] if topic_sentence_items else None
        
        bullet_points = [point.strip() for point in temp_memory.get("Bullet Points", []) if point.strip()]
        
        template_flow_items = [item for item in temp_memory.get("Template Flow", []) if item.strip()]
        template = "\n".join(template_flow_items) if template_flow_items else None

        # Get key ideas from project memory for context
        project_key_ideas = project_memory.get("Key Ideas", [])
        project_previous_content = project_memory.get("Previous Content", [])
        
        # Build prompt with minimal redundancy
        prompt_parts: List[str] = [
            "You are an expert research writer. Produce exactly one cohesive academic paragraph using only the information below."
        ]
        
        self._append_prompt_section(prompt_parts, "Writing Context", writing_context)
        self._append_prompt_section(prompt_parts, "Project Key Ideas", project_key_ideas[:5], bulletize=True)
        self._append_prompt_section(prompt_parts, "Topic Sentence", topic_sentence)
        self._append_prompt_section(prompt_parts, "Bullet Points", bullet_points, bulletize=True)
        self._append_prompt_section(prompt_parts, "Template Flow", template)
        
        self._append_prompt_section(prompt_parts, "Recent Project Content", project_previous_content[:3], bulletize=True)
        
        requirements: List[str] = []
        requirements.append("Write a new standalone paragraph (ignore any previously drafted text).")
        
        if topic_sentence:
            requirements.append("Incorporate the provided topic sentence (or a refined variant) near the beginning.")
        if bullet_points:
            requirements.append("Cover every bullet point with specific evidence or reasoning.")
        if template:
            requirements.append("Follow the template flow order when developing the paragraph.")
        requirements.append("Maintain scholarly tone, smooth transitions, and precise language.")
        requirements.append("Return only the finalized paragraph (no explanations or lists).")
        
        self._append_prompt_section(prompt_parts, "Output Requirements", [f"- {req}" for req in requirements])
        
        prompt = "\n".join(prompt_parts).strip() + "\n"
        
        # Save prompt for auditing/debugging
        self._save_prompt(prompt, mode="NewParagraph")
        
        # Generate plain text paragraph
        plain_text = self.ai_wrapper.generate(prompt)
        
        # Remove any inline comments that might have been generated (shouldn't happen, but just in case)
        plain_text, _ = self._extract_inline_comments(plain_text)
        
        # Convert to LaTeX format
        latex_text = self._convert_to_latex(plain_text)
        
        # Save to files
        self._append_to_history(plain_text)
        self._save_latex(latex_text)
        
        # Save output to TempMemory.txt Output section
        self._save_output_to_temp_memory(plain_text)
        
        return {
            'plain_text': plain_text,
            'latex': latex_text
        }
    
    def revise_paragraph(self) -> Dict[str, Any]:
        """
        ReviseParagraph mode: Revise an existing paragraph based on revision feedback and input from TempMemory.txt.
        
        Reads from TempMemory.txt which contains:
        - Writing Context: The task/context for writing
        - Current Paragraph: The current paragraph to revise
        - Revision Feedback: Feedback on what needs to be changed
        - Topic Sentence: (Optional) Topic sentence to incorporate
        - Bullet Points: (Optional) Bullet points to expand on
        - Template Flow: (Optional) Template describing the logic flow
        
        Outputs:
        - Plain text to WritingHistory.txt with version number
        - LaTeX to Output/Latex.txt
        - Revised paragraph to TempMemory.txt Output section
        
        Returns:
            Dictionary with 'plain_text', 'latex', and 'version' keys
        """
        # Load memory from TempMemory.txt
        temp_memory = self.memory_manager.load_temp_memory(str(self.temp_memory_file))
        
        # Load project memory for context
        project_memory = self.memory_manager.load_project_memory(str(self.project_memory_file))
        
        # Extract components from TempMemory
        writing_context_items = temp_memory.get("Writing Context", [])
        writing_context = "\n".join(writing_context_items) if writing_context_items else None
        
        current_paragraph_items = temp_memory.get("Current Paragraph", [])
        current_paragraph_raw = "\n".join(current_paragraph_items) if current_paragraph_items else None
        
        # Extract inline comments from Current Paragraph and remove them
        inline_comments: List[Dict[str, str]] = []
        if current_paragraph_raw:
            current_paragraph, inline_comments = self._extract_inline_comments(current_paragraph_raw)
        else:
            current_paragraph = None
        
        revision_feedback_items = temp_memory.get("Revision Feedback", [])
        revision_feedback = "\n".join(revision_feedback_items) if revision_feedback_items else None
        
        # Combine inline comments with existing revision feedback (without duplicating content)
        inline_feedback_lines: List[str] = self._format_inline_feedback(inline_comments)
        if inline_feedback_lines and (not revision_feedback or not revision_feedback.strip()):
            revision_feedback = "Address every inline comment listed below."
        
        topic_sentence_items = temp_memory.get("Topic Sentence", [])
        topic_sentence = topic_sentence_items[0] if topic_sentence_items else None
        
        bullet_points = temp_memory.get("Bullet Points", [])
        
        template_flow_items = temp_memory.get("Template Flow", [])
        template = "\n".join(template_flow_items) if template_flow_items else None
        
        # Validate required inputs
        if not current_paragraph or not current_paragraph.strip():
            raise ValueError("Current Paragraph is required in TempMemory.txt for ReviseParagraph mode")
        
        # Revision feedback can come from either the Revision Feedback section or inline comments
        if not revision_feedback or not revision_feedback.strip():
            raise ValueError("Revision Feedback is required in TempMemory.txt for ReviseParagraph mode (or provide inline comments in Current Paragraph using {comment} format)")
        
        # Get key ideas from project memory for context
        project_key_ideas = project_memory.get("Key Ideas", [])
        project_previous_content = project_memory.get("Previous Content", [])
        
        # Build concise revision prompt
        prompt_parts: List[str] = [
            "You are revising the following academic paragraph. Apply the feedback carefully and return one improved paragraph."
        ]
        
        self._append_prompt_section(prompt_parts, "Writing Context", writing_context)
        self._append_prompt_section(prompt_parts, "Current Paragraph", current_paragraph)
        self._append_prompt_section(prompt_parts, "Revision Feedback", revision_feedback)
        self._append_prompt_section(
            prompt_parts,
            "Inline Comments (sentence-specific)",
            inline_feedback_lines
        )
        self._append_prompt_section(prompt_parts, "Project Key Ideas", project_key_ideas[:5], bulletize=True)
        self._append_prompt_section(prompt_parts, "Topic Sentence", topic_sentence)
        filtered_bullets = [bp.strip() for bp in bullet_points if bp.strip()]
        self._append_prompt_section(prompt_parts, "Bullet Points", filtered_bullets, bulletize=True)
        self._append_prompt_section(prompt_parts, "Template Flow", template)
        self._append_prompt_section(prompt_parts, "Recent Project Content", project_previous_content[:3], bulletize=True)
        
        requirements: List[str] = [
            "Resolve every item in the revision feedback before returning the paragraph."
        ]
        if inline_feedback_lines:
            requirements.append("Ensure each inline comment's sentence reflects the requested change.")
        if topic_sentence:
            requirements.append("Keep the topic sentence consistent with the provided guidance.")
        if filtered_bullets:
            requirements.append("Address every bullet point with concrete detail or logic.")
        if template:
            requirements.append("Honor the template flow order when restructuring content.")
        requirements.append("Preserve the original meaning and claims while improving clarity and flow.")
        requirements.append("Return only the revised paragraph text (no explanations).")
        
        self._append_prompt_section(prompt_parts, "Output Requirements", [f"- {req}" for req in requirements])
        
        prompt = "\n".join(prompt_parts).strip() + "\n"
        
        # Save prompt for auditing/debugging
        self._save_prompt(prompt, mode="ReviseParagraph")
        
        # Generate revised paragraph
        plain_text = self.ai_wrapper.generate(prompt)
        
        # Remove any inline comments that might have been generated (shouldn't happen, but just in case)
        plain_text, _ = self._extract_inline_comments(plain_text)
        
        # Convert to LaTeX format
        latex_text = self._convert_to_latex(plain_text)
        
        # Save to files with version number
        version = self._append_to_history_with_version(plain_text, mode="ReviseParagraph")
        self._save_latex(latex_text)
        
        # Save output to TempMemory.txt Output section
        self._save_output_to_temp_memory(plain_text)
        
        return {
            'plain_text': plain_text,
            'latex': latex_text,
            'version': version
        }
    
    def _extract_inline_comments(self, text: str) -> tuple[str, List[Dict[str, str]]]:
        """
        Extract inline comments from text that are enclosed in curly braces {}.
        
        Inline comments are used to provide revision feedback directly in the text.
        Example: "This sentence needs work. {Make it more concise and clear.}"
        
        Args:
            text: Text that may contain inline comments like {comment text}
            
        Returns:
            Tuple of (text_without_comments, list_of_comment_dicts)
        """
        pattern = r'\{([^}]*)\}'
        comments: List[Dict[str, str]] = []
        cleaned_parts: List[str] = []
        last_index = 0
        
        for match in re.finditer(pattern, text):
            start, end = match.span()
            cleaned_parts.append(text[last_index:start])
            
            comment_text = match.group(1).strip()
            if comment_text:
                target_sentence = self._get_sentence_for_comment(text, start)
                comments.append({
                    "comment": comment_text,
                    "target_sentence": target_sentence
                })
            
            last_index = end
        
        cleaned_parts.append(text[last_index:])
        text_without_comments = ''.join(cleaned_parts)
        
        # Clean up extra whitespace (multiple spaces/newlines)
        text_without_comments = re.sub(r' +', ' ', text_without_comments)
        text_without_comments = re.sub(r'\n\s*\n+', '\n\n', text_without_comments)
        text_without_comments = text_without_comments.strip()
        
        return text_without_comments, comments

    def _get_sentence_for_comment(self, text: str, comment_start: int) -> str:
        """
        Best-effort extraction of the sentence (or clause) immediately preceding an inline comment.
        This helps the AI model understand exactly which sentence the inline feedback refers to.
        """
        preceding_text = text[:comment_start]
        
        sentence_start = 0
        for i in range(len(preceding_text) - 1, -1, -1):
            if preceding_text[i] in '.?!\n':
                sentence_start = i + 1
                break
        
        sentence = preceding_text[sentence_start:].strip()
        
        if not sentence:
            sentence = preceding_text[-200:].strip()
        
        return sentence
    
    def _convert_to_latex(self, text: str) -> str:
        """
        Convert plain text to LaTeX format.
        This is a basic conversion - can be enhanced with AI if needed.
        """
        # Basic LaTeX conversion
        # Escape LaTeX special characters
        latex = text.replace('\\', '\\textbackslash{}')
        latex = latex.replace('&', '\\&')
        latex = latex.replace('%', '\\%')
        latex = latex.replace('$', '\\$')
        latex = latex.replace('#', '\\#')
        latex = latex.replace('^', '\\textasciicircum{}')
        latex = latex.replace('_', '\\_')
        latex = latex.replace('{', '\\{')
        latex = latex.replace('}', '\\}')
        latex = latex.replace('~', '\\textasciitilde{}')
        
        # Try to use AI for better LaTeX conversion if available
        try:
            conversion_prompt = f"""Convert the following academic text to LaTeX format. 
Preserve the meaning and structure. Use appropriate LaTeX commands for formatting.

Text:
{text}

Output only the LaTeX code, without any explanations or markdown formatting."""
            
            ai_latex = self.ai_wrapper.generate(conversion_prompt)
            # Clean up AI output (remove markdown code blocks if present)
            ai_latex = ai_latex.strip()
            if ai_latex.startswith('```'):
                lines = ai_latex.split('\n')
                ai_latex = '\n'.join(lines[1:-1]) if lines[-1].startswith('```') else '\n'.join(lines[1:])
            
            return ai_latex.strip()
        except Exception:
            # Fallback to basic conversion
            return latex
    
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
        
        Note: This is a legacy method. For new implementations, use the appropriate mode.
        
        Args:
            paragraph_template: Optional paragraph template
            
        Returns:
            Revised paragraph text
        """
        # Load todo history
        if not self.todo_history_file.exists():
            raise ValueError(f"Todo history file not found: {self.todo_history_file}")
        
        # Read todo list
        with open(self.todo_history_file, 'r', encoding='utf-8') as f:
            todo_content = f.read()
        
        # Load writing history for context
        writing_history = ""
        if self.writing_history_file.exists():
            with open(self.writing_history_file, 'r', encoding='utf-8') as f:
                writing_history = f.read()
        
        # Create revision prompt
        prompt = f"""Revise the following paragraph based on the todo list feedback:

===== Current Writing =====
{writing_history[-2000:]}  # Last 2000 chars for context

===== Todo List =====
{todo_content}

Please revise the writing to address all items in the todo list.
"""
        
        revised_text = self.ai_wrapper.generate(prompt)
        
        # Save to output
        self._save_output(revised_text)
        
        return revised_text
    
    def _append_to_history(self, text: str):
        """Append text to writing history."""
        self.writing_history_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.writing_history_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Entry: {timestamp}\n")
            f.write(f"{'='*80}\n\n")
            f.write(text)
            f.write("\n\n")
    
    def _get_next_version_number(self) -> int:
        """
        Get the next version number for WritingHistory.txt.
        
        Returns:
            Next version number (starts at 1 if no versions exist)
        """
        if not self.writing_history_file.exists():
            return 1
        
        with open(self.writing_history_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all version numbers in the file
        version_pattern = r'Version\s+(\d+)'
        versions = re.findall(version_pattern, content, re.IGNORECASE)
        
        if not versions:
            return 1
        
        # Return the highest version number + 1
        max_version = max(int(v) for v in versions)
        return max_version + 1
    
    def _append_to_history_with_version(self, text: str, mode: str = "ReviseParagraph") -> int:
        """
        Append text to writing history with version number.
        
        Args:
            text: Text to append
            mode: Writing mode (e.g., "ReviseParagraph", "NewParagraph")
            
        Returns:
            Version number assigned to this entry
        """
        self.writing_history_file.parent.mkdir(parents=True, exist_ok=True)
        
        version = self._get_next_version_number()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.writing_history_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"Version {version} - {mode} - {timestamp}\n")
            f.write(f"{'='*80}\n\n")
            f.write(text)
            f.write("\n\n")
        
        return version
    
    def _save_latex(self, latex_text: str):
        """Save LaTeX text to Latex.txt."""
        self.output_latex.parent.mkdir(parents=True, exist_ok=True)
        
        # Overwrite with latest LaTeX output
        with open(self.output_latex, 'w', encoding='utf-8') as f:
            f.write(latex_text)
            f.write("\n")
    
    def _save_plaintext(self, text: str):
        """Save plain text to Plaintext.txt."""
        self.output_plaintext.parent.mkdir(parents=True, exist_ok=True)
        
        # Overwrite with latest plain text output
        with open(self.output_plaintext, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def _save_prompt(self, prompt: str, mode: str):
        """
        Save the exact prompt sent to the AI into prompt.txt for debugging/auditing.
        
        Args:
            prompt: The prompt text that will be sent to the AI model
            mode: The writer mode (e.g., "NewParagraph", "ReviseParagraph")
        """
        self.prompt_history_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = []
        entry.append(f"{'='*80}")
        entry.append(f"Mode: {mode} | Timestamp: {timestamp}")
        entry.append(f"{'='*80}")
        entry.append(prompt.rstrip())
        entry.append("")  # blank line separator
        entry_text = "\n".join(entry) + "\n"
        
        existing_content = ""
        if self.prompt_history_file.exists():
            with open(self.prompt_history_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        with open(self.prompt_history_file, 'w', encoding='utf-8') as f:
            if existing_content:
                f.write(entry_text + existing_content)
            else:
                f.write(entry_text)
    
    def _save_output_to_temp_memory(self, output_text: str):
        """
        Save the resulting paragraph to TempMemory.txt Output section.
        
        Args:
            output_text: The paragraph text to save
        """
        # Load current temp memory
        temp_memory = self.memory_manager.load_temp_memory(str(self.temp_memory_file))
        
        # Update the Output section with the new paragraph
        # Split the text into lines and store as list items
        output_lines = [line.strip() for line in output_text.strip().split('\n') if line.strip()]
        temp_memory["Output"] = output_lines
        
        # Save back to file
        self.memory_manager.save_temp_memory(str(self.temp_memory_file), temp_memory)
    
    def _append_prompt_section(
        self,
        prompt_parts: List[str],
        title: str,
        content: Optional[Union[str, List[str]]],
        bulletize: bool = False
    ):
        """
        Append a formatted section to the prompt if content is provided.
        """
        if content is None:
            return
        
        if isinstance(content, list):
            entries = [str(item).strip() for item in content if str(item).strip()]
            if not entries:
                return
        else:
            content_str = str(content).strip()
            if not content_str:
                return
            entries = content_str.splitlines()
        
        prompt_parts.append(f"===== {title} =====")
        for entry in entries:
            if bulletize:
                if entry.startswith(("-", "•")):
                    prompt_parts.append(entry)
                else:
                    prompt_parts.append(f"- {entry}")
            else:
                prompt_parts.append(entry)
        prompt_parts.append("")
    
    def _format_inline_feedback(self, inline_comments: List[Dict[str, str]]) -> List[str]:
        """
        Format inline comments into a readable string that ties each comment to its sentence.
        """
        if not inline_comments:
            return []
        
        lines: List[str] = []
        for idx, entry in enumerate(inline_comments, start=1):
            sentence = entry.get("target_sentence", "").strip()
            comment = entry.get("comment", "").strip()
            
            if sentence:
                lines.append(f"{idx}. Sentence: {sentence}")
                lines.append(f"   Feedback: {comment}")
            else:
                lines.append(f"{idx}. Feedback: {comment}")
        
        return lines
    
    def _save_output(self, text: str):
        """Save text to output files (legacy method for backward compatibility)."""
        # Save to Plaintext.txt
        self._save_plaintext(text)
        
        # Also save LaTeX version
        latex_text = self._convert_to_latex(text)
        self._save_latex(latex_text)


def main():
    """Command-line interface for Writer."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Writer with multiple modes for research paper writing'
    )
    parser.add_argument('project_path', help='Project name (e.g., "MyProject" - will look in projects/ directory)')
    parser.add_argument('--mode', '-m', default='newparagraph',
                       choices=['newparagraph', 'reviseparagraph'],
                       help='Writing mode (default: newparagraph)')
    parser.add_argument('--provider', default='gemini', choices=['gemini', 'openai'],
                       help='API provider (default: gemini)')
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_key = os.getenv("GEMINI_API_KEY") if args.provider == "gemini" else None
    openai_key = os.getenv("OPENAI_API_KEY") if args.provider == "openai" else None
    
    # project_path will be automatically prepended with "projects/" in Writer.__init__
    writer = Writer(
        project_path=args.project_path,
        api_provider=args.provider,
        gemini_api_key=gemini_key,
        openai_api_key=openai_key
    )
    
    try:
        if args.mode == 'newparagraph':
            result = writer.new_paragraph()
            print("✓ Paragraph written!")
            print(f"\nPlain text saved to: {writer.writing_history_file}")
            print(f"LaTeX saved to: {writer.output_latex}")
            print("\nGenerated paragraph (plain text):")
            print("-" * 80)
            print(result['plain_text'])
            print("-" * 80)
        elif args.mode == 'reviseparagraph':
            result = writer.revise_paragraph()
            print("✓ Paragraph revised!")
            print(f"\nVersion {result['version']} saved to: {writer.writing_history_file}")
            print(f"LaTeX saved to: {writer.output_latex}")
            print("\nRevised paragraph (plain text):")
            print("-" * 80)
            print(result['plain_text'])
            print("-" * 80)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
