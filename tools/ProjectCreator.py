"""
Project Creator Utility

This utility creates a new project folder structure under the Projects directory
with all necessary subdirectories and initial files for a research paper project.

Usage:
    # Command-line interface
    python tools/ProjectCreator.py "MyResearchProject"
    
    # Or as a module
    python -m tools.ProjectCreator "MyResearchProject"
    
    # Or programmatically
    from tools import ProjectCreator
    creator = ProjectCreator()
    project_dir = creator.create_project("MyResearchProject")

Project Structure Created:
    projects/
    └── [project_name]/
        ├── Memory/
        │   ├── ProjectMemory.txt      # Key ideas, previous content, outlines
        │   └── TempMemory.txt          # Temporary revision feedback
        ├── Intermediate/
        │   ├── WritingHistory.txt      # Writing history log
        │   └── TodoHistory.txt         # Todo list history
        └── Output/
            ├── Plaintext.txt           # Plain text output
            ├── Latex.txt               # LaTeX output
            └── StagedOutput.txt        # Staged output
"""

import os
from pathlib import Path
from typing import Optional


class ProjectCreator:
    """Utility to create new project folder structure."""
    
    def __init__(self, projects_base_dir: str = "projects"):
        """Initialize with projects base directory (default: "projects")."""
        self.projects_base_dir = Path(projects_base_dir)
        self.projects_base_dir.mkdir(exist_ok=True)
    
    def create_project(self, project_name: str) -> Path:
        """Create a new project folder structure with all necessary files."""
        # Create project directory
        project_dir = self.projects_base_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Memory directory
        project_memory_dir = project_dir / "Memory"
        project_memory_dir.mkdir(exist_ok=True)
        
        # Create ProjectMemory.txt
        project_memory_file = project_memory_dir / "ProjectMemory.txt"
        if not project_memory_file.exists():
            with open(project_memory_file, 'w', encoding='utf-8') as f:
                f.write("===== Key Ideas =====\n\n")
                f.write("===== Previous Content =====\n\n")
                f.write("===== Outlines =====\n\n")
        
        # Create TempMemory.txt
        temp_memory_file = project_memory_dir / "TempMemory.txt"
        if not temp_memory_file.exists():
            with open(temp_memory_file, 'w', encoding='utf-8') as f:
                f.write("===== Revision Feedback =====\n\n")
        
        # Create Intermediate directory
        intermediate_dir = project_dir / "Intermediate"
        intermediate_dir.mkdir(exist_ok=True)
        
        # Create WritingHistory.txt
        writing_history_file = intermediate_dir / "WritingHistory.txt"
        if not writing_history_file.exists():
            with open(writing_history_file, 'w', encoding='utf-8') as f:
                f.write("===== Writing History =====\n\n")
        
        # Create TodoHistory.txt
        todo_history_file = intermediate_dir / "TodoHistory.txt"
        if not todo_history_file.exists():
            with open(todo_history_file, 'w', encoding='utf-8') as f:
                f.write("===== Todo History =====\n\n")
        
        # Create Output directory
        output_dir = project_dir / "Output"
        output_dir.mkdir(exist_ok=True)
        
        # Create Plaintext.txt
        plaintext_file = output_dir / "Plaintext.txt"
        if not plaintext_file.exists():
            with open(plaintext_file, 'w', encoding='utf-8') as f:
                f.write("")
        
        # Create Latex.txt
        latex_file = output_dir / "Latex.txt"
        if not latex_file.exists():
            with open(latex_file, 'w', encoding='utf-8') as f:
                f.write("")
        
        # Create StagedOutput.txt
        staged_output_file = output_dir / "StagedOutput.txt"
        if not staged_output_file.exists():
            with open(staged_output_file, 'w', encoding='utf-8') as f:
                f.write("")
        
        print(f"✓ Project '{project_name}' created successfully!")
        print(f"  Project directory: {project_dir}")
        print(f"  Structure:")
        print(f"    - Memory/")
        print(f"      - ProjectMemory.txt")
        print(f"      - TempMemory.txt")
        print(f"    - Intermediate/")
        print(f"      - WritingHistory.txt")
        print(f"      - TodoHistory.txt")
        print(f"    - Output/")
        print(f"      - Plaintext.txt")
        print(f"      - Latex.txt")
        print(f"      - StagedOutput.txt")
        
        return project_dir


def main():
    """Command-line interface for ProjectCreator."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ProjectCreator.py <project_name>")
        print("   or: python -m tools.ProjectCreator <project_name>")
        print("\nExamples:")
        print('  python tools/ProjectCreator.py "MyResearchPaper"')
        print('  python -m tools.ProjectCreator "My Paper"')
        print("\nThis will create a project structure at:")
        print("  projects/<project_name>/")
        sys.exit(1)
    
    project_name = sys.argv[1]
    
    creator = ProjectCreator()
    try:
        creator.create_project(project_name)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

