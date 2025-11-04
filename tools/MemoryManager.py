"""
Memory Manager
Manages three levels of memory:
- Global memory: Writing heuristics (from global_memory.txt)
- Single paper memory: Key ideas for the paper, potential paper reviews (from ProjectMemory.txt)
- Single paragraph memory: Templates, the paper (from TempMemory.txt for revisions)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import re

# Handle imports when run as script or module
try:
    from .CloudAIWrapper import CloudAIWrapper
except ImportError:
    # Add parent directory to path when run as script
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from tools.CloudAIWrapper import CloudAIWrapper


class MemoryManager:
    """Manages multi-level memory for paper writing."""
    
    def __init__(self, global_memory_file: str = "global_memory.txt"):
        """
        Initialize MemoryManager.
        
        Args:
            global_memory_file: Path to global memory file (default: "global_memory.txt")
        """
        self.global_memory_file = Path(global_memory_file)
        self.global_memory = {}
        self._load_global_memory()
    
    def _load_global_memory(self):
        """Load global memory from file."""
        if self.global_memory_file.exists():
            with open(self.global_memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.global_memory = self._parse_memory_file(content)
        else:
            # Create default global memory
            self.global_memory = {
                "Writing Heuristics": [
                    "Clarity: Ensure ideas are clearly expressed",
                    "Structure: Follow logical flow",
                    "Academic Tone: Maintain formal academic style",
                    "Evidence: Support claims with evidence",
                    "Coherence: Ensure smooth transitions"
                ]
            }
    
    def _parse_memory_file(self, content: str) -> Dict[str, List[str]]:
        """
        Parse memory file content into structured format.
        
        Format:
        ===== Section Name =====
        - Item 1
        - Item 2
        
        Args:
            content: File content
            
        Returns:
            Dictionary mapping section names to lists of items
        """
        sections = {}
        current_section = None
        current_items = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Check for section header
            if line.startswith('=====') and line.endswith('====='):
                # Save previous section
                if current_section:
                    sections[current_section] = current_items
                
                # Start new section
                current_section = line.replace('=', '').strip()
                current_items = []
            elif line.startswith('•') or line.startswith('-'):
                # List item (bullet or dash)
                item = line.lstrip('•- ').strip()
                if item:
                    current_items.append(item)
        
        # Save last section
        if current_section:
            sections[current_section] = current_items
        
        return sections
    
    def get_global_memory(self) -> Dict[str, List[str]]:
        """
        Get global memory (writing heuristics).
        
        Returns:
            Dictionary of global memory sections
        """
        return self.global_memory.copy()
    
    def get_heuristics(self) -> List[str]:
        """
        Get writing heuristics from global memory.
        
        Returns:
            List of heuristics
        """
        return self.global_memory.get("Writing Heuristics", [])
    
    def load_project_memory(self, project_memory_file: str) -> Dict[str, List[str]]:
        """
        Load single paper memory from project memory file.
        
        ProjectMemory.txt contains two sections:
        - Key Ideas: Key ideas for the paper
        - Previous Content: Previous content from the paper
        
        Args:
            project_memory_file: Path to ProjectMemory.txt
            
        Returns:
            Dictionary of project memory sections with keys: "Key Ideas", "Previous Content"
        """
        project_memory_file = Path(project_memory_file)
        if not project_memory_file.exists():
            return {
                "Key Ideas": [],
                "Previous Content": []
            }
        
        with open(project_memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            parsed = self._parse_memory_file(content)
        
        # Ensure only the two required sections are returned
        return {
            "Key Ideas": parsed.get("Key Ideas", []),
            "Previous Content": parsed.get("Previous Content", [])
        }
    
    def load_temp_memory(self, temp_memory_file: str) -> Dict[str, List[str]]:
        """
        Load single paragraph memory from temp memory file.
        
        TempMemory.txt contains four sections:
        - Topic Sentence: The topic sentence for the paragraph
        - Bullet Points: Bullet points to expand on
        - Template Flow: Template describing the logic flow
        - Current Paragraph: Current paragraph content (for revision)
        
        Args:
            temp_memory_file: Path to TempMemory.txt
            
        Returns:
            Dictionary of temp memory sections with keys: "Topic Sentence", "Bullet Points", "Template Flow", "Current Paragraph"
        """
        temp_memory_file = Path(temp_memory_file)
        if not temp_memory_file.exists():
            return {
                "Topic Sentence": [],
                "Bullet Points": [],
                "Template Flow": [],
                "Current Paragraph": []
            }
        
        with open(temp_memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            parsed = self._parse_memory_file(content)
        
        # Return the four required sections plus optional Revision Feedback
        return {
            "Topic Sentence": parsed.get("Topic Sentence", []),
            "Bullet Points": parsed.get("Bullet Points", []),
            "Template Flow": parsed.get("Template Flow", []),
            "Current Paragraph": parsed.get("Current Paragraph", []),
            "Revision Feedback": parsed.get("Revision Feedback", [])  # Optional section
        }
    
    def save_project_memory(self, project_memory_file: str, memory: Dict[str, List[str]]):
        """
        Save project memory to file.
        
        ProjectMemory.txt contains two sections (in order):
        - Key Ideas
        - Previous Content
        
        Args:
            project_memory_file: Path to ProjectMemory.txt
            memory: Dictionary of memory sections with keys: "Key Ideas", "Previous Content"
        """
        project_memory_file = Path(project_memory_file)
        project_memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Define the required sections in order
        required_sections = ["Key Ideas", "Previous Content"]
        
        with open(project_memory_file, 'w', encoding='utf-8') as f:
            for section_name in required_sections:
                items = memory.get(section_name, [])
                f.write(f"===== {section_name} =====\n")
                f.write("\n")
                for item in items:
                    f.write(f"- {item}\n")
                f.write("\n")
    
    def save_temp_memory(self, temp_memory_file: str, memory: Dict[str, List[str]]):
        """
        Save temp memory to file.
        
        TempMemory.txt contains four sections (in order):
        - Topic Sentence
        - Bullet Points
        - Template Flow
        - Current Paragraph
        
        Args:
            temp_memory_file: Path to TempMemory.txt
            memory: Dictionary of memory sections with keys: "Topic Sentence", "Bullet Points", "Template Flow", "Current Paragraph"
        """
        temp_memory_file = Path(temp_memory_file)
        temp_memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Define the required sections in order (Revision Feedback is optional)
        required_sections = ["Topic Sentence", "Bullet Points", "Template Flow", "Current Paragraph", "Revision Feedback"]
        
        with open(temp_memory_file, 'w', encoding='utf-8') as f:
            for section_name in required_sections:
                items = memory.get(section_name, [])
                f.write(f"===== {section_name} =====\n")
                f.write("\n")
                for item in items:
                    f.write(f"- {item}\n")
                f.write("\n")
    
    def get_all_memory(self, project_memory_file: Optional[str] = None,
                      temp_memory_file: Optional[str] = None) -> Dict[str, Dict[str, List[str]]]:
        """
        Get all three levels of memory.
        
        Args:
            project_memory_file: Optional path to ProjectMemory.txt
            temp_memory_file: Optional path to TempMemory.txt
            
        Returns:
            Dictionary with 'global', 'project', and 'temp' keys
        """
        result = {
            'global': self.get_global_memory()
        }
        
        if project_memory_file:
            result['project'] = self.load_project_memory(project_memory_file)
        
        if temp_memory_file:
            result['temp'] = self.load_temp_memory(temp_memory_file)
        
        return result
    
    def summarize_staged_output(self, staged_output_file: str,
                                api_provider: str = "gemini",
                                gemini_api_key: Optional[str] = None,
                                openai_api_key: Optional[str] = None) -> List[str]:
        """
        Summarize content in StagedOutput.txt into 10 diverse, important sentences.
        
        This function reads the StagedOutput.txt file and uses AI to extract the 10 most
        important sentences that capture diverse ideas from the draft. The sentences are
        selected to maximize coverage of different concepts and topics.
        
        Args:
            staged_output_file: Path to StagedOutput.txt file
            api_provider: AI provider to use ("gemini" or "openai", default: "gemini")
            gemini_api_key: Optional Gemini API key (defaults to GEMINI_API_KEY env var)
            openai_api_key: Optional OpenAI API key (defaults to OPENAI_API_KEY env var)
            
        Returns:
            List of 10 sentences summarizing the most important and diverse ideas
            
        Raises:
            FileNotFoundError: If StagedOutput.txt doesn't exist
            ValueError: If AI provider is not available
        """
        staged_output_path = Path(staged_output_file)
        if not staged_output_path.exists():
            raise FileNotFoundError(f"StagedOutput.txt not found at: {staged_output_file}")
        
        # Read the staged output content
        with open(staged_output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            return []
        
        # Initialize AI wrapper
        ai_wrapper = CloudAIWrapper(
            provider=api_provider,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key
        )
        
        # Create prompt for summarization
        prompt = f"""You are analyzing a research paper draft. Extract exactly 10 sentences that are the most important and diverse.

The sentences should:
1. Capture the most critical ideas and contributions
2. Be as diverse as possible - covering different topics, concepts, and aspects
3. Represent distinct ideas rather than repeating similar points
4. Be complete, meaningful sentences from the draft

IMPORTANT: Output ONLY the sentences themselves. Do NOT include any introductory text, instructions, or explanations like "Here are 10 sentences:" or "The following are:". Just list the sentences directly.

Here is the draft content:

{content}

Please output exactly 10 sentences, one per line, as a numbered list (1. sentence, 2. sentence, etc.). Do not include any preface or instruction text."""
        
        # Generate summary using AI
        try:
            summary_text = ai_wrapper.generate(prompt)
            
            # Parse the output to extract sentences
            sentences = []
            
            # Patterns to identify instruction/metadata sentences
            instruction_patterns = [
                r'^here are \d+',
                r'^the following are',
                r'^these are \d+',
                r'^below are \d+',
                r'^here are the \d+',
                r'^the \d+ (most important|diverse|sentences)',
                r'^these (sentences|are)',
                r'^following are',
                r'^extracted (sentences|from)',
                r'^(these|the) (sentences|following)',
            ]
            
            for line in summary_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Remove numbering (e.g., "1. ", "1)", "- ", etc.)
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                line = re.sub(r'^-\s*', '', line)
                line = line.strip()
                
                # Skip empty or very short lines
                if not line or len(line) < 20:
                    continue
                
                # Check if line is an instruction sentence
                line_lower = line.lower()
                is_instruction = any(re.search(pattern, line_lower) for pattern in instruction_patterns)
                
                # Skip instruction sentences and lines that seem like metadata
                if is_instruction:
                    continue
                
                # Skip lines that are just colons or separators
                if line.strip() in [':', '-', '—', '•']:
                    continue
                
                sentences.append(line)
            
            # Return exactly 10 sentences (or all if fewer)
            return sentences[:10]
            
        except Exception as e:
            raise ValueError(f"Failed to generate summary: {e}")


def main():
    """
    Command-line interface for updating project memory from StagedOutput.txt.
    
    Usage:
        python -m tools.MemoryManager <project_name>
        python tools/MemoryManager.py privacypowder
    
    Examples:
        python -m tools.MemoryManager privacypowder
        python tools/MemoryManager.py projects/privacypowder
        python -m tools.MemoryManager privacypowder --provider gemini
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m tools.MemoryManager <project_name>")
        print("   or: python tools/MemoryManager.py <project_name>")
        print("\nExamples:")
        print('  python -m tools.MemoryManager privacypowder')
        print('  python tools/MemoryManager.py projects/privacypowder')
        print("\nOptions:")
        print('  --provider gemini|openai  AI provider to use (default: gemini)')
        print("\nThis will:")
        print("  1. Summarize StagedOutput.txt into 10 diverse sentences")
        print("  2. Update ProjectMemory.txt 'Previous Content' section")
        sys.exit(1)
    
    project_path = sys.argv[1]
    api_provider = "gemini"
    
    # Check for provider option
    if len(sys.argv) > 2:
        if sys.argv[2] == "--provider" and len(sys.argv) > 3:
            api_provider = sys.argv[3]
        elif sys.argv[2] in ["gemini", "openai"]:
            api_provider = sys.argv[2]
    
    # Normalize project path
    if not project_path.startswith("projects/"):
        project_path = f"projects/{project_path}"
    
    project_dir = Path(project_path)
    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_path}")
        print(f"  Expected: {project_dir.absolute()}")
        sys.exit(1)
    
    staged_output_file = project_dir / "Output" / "StagedOutput.txt"
    project_memory_file = project_dir / "Memory" / "ProjectMemory.txt"
    
    if not staged_output_file.exists():
        print(f"Error: StagedOutput.txt not found: {staged_output_file}")
        sys.exit(1)
    
    if not project_memory_file.exists():
        print(f"Error: ProjectMemory.txt not found: {project_memory_file}")
        sys.exit(1)
    
    print(f"Project: {project_path}")
    print(f"StagedOutput: {staged_output_file}")
    print(f"ProjectMemory: {project_memory_file}")
    print()
    
    # Initialize memory manager
    mm = MemoryManager()
    
    # Summarize StagedOutput.txt
    print("Summarizing StagedOutput.txt...")
    try:
        sentences = mm.summarize_staged_output(
            str(staged_output_file),
            api_provider=api_provider
        )
        
        if not sentences:
            print("Warning: No sentences extracted from StagedOutput.txt")
            sys.exit(0)
        
        print(f"✓ Extracted {len(sentences)} sentences:")
        for i, sentence in enumerate(sentences, 1):
            preview = sentence[:80] + "..." if len(sentence) > 80 else sentence
            print(f"  {i}. {preview}")
        print()
        
    except Exception as e:
        print(f"Error: Failed to summarize StagedOutput.txt: {e}")
        sys.exit(1)
    
    # Load existing project memory
    print("Loading existing ProjectMemory.txt...")
    memory = mm.load_project_memory(str(project_memory_file))
    
    # Update "Previous Content" section with summarized sentences
    print("Updating 'Previous Content' section...")
    memory["Previous Content"] = sentences
    
    # Save updated memory
    print("Saving updated ProjectMemory.txt...")
    mm.save_project_memory(str(project_memory_file), memory)
    
    print()
    print("✓ Successfully updated ProjectMemory.txt!")
    print(f"  Added {len(sentences)} sentences to 'Previous Content' section")


if __name__ == "__main__":
    main()

