"""
Create New Project Utility
Creates a new project folder structure under the Projects directory.
"""

import os
from pathlib import Path
from typing import Optional


class CreateNewProject:
    """Utility to create new project folder structure."""
    
    def __init__(self, projects_base_dir: str = "Projects"):
        """
        Initialize CreateNewProject utility.
        
        Args:
            projects_base_dir: Base directory for projects (default: "Projects")
        """
        self.projects_base_dir = Path(projects_base_dir)
        self.projects_base_dir.mkdir(exist_ok=True)
    
    def create_project(self, project_name: str) -> Path:
        """
        Create a new project folder structure.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Path to the created project directory
        """
        # Create project directory
        project_dir = self.projects_base_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Project Memory directory
        project_memory_dir = project_dir / "Project Memory"
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
        
        # Create AutoWritingHistory.txt
        writing_history_file = intermediate_dir / "AutoWritingHistory.txt"
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
        
        # Create plaintext.txt
        plaintext_file = output_dir / "plaintext.txt"
        if not plaintext_file.exists():
            with open(plaintext_file, 'w', encoding='utf-8') as f:
                f.write("")
        
        # Create output.txt
        output_file = output_dir / "output.txt"
        if not output_file.exists():
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("")
        
        print(f"✓ Project '{project_name}' created successfully!")
        print(f"  Project directory: {project_dir}")
        print(f"  Structure:")
        print(f"    - Project Memory/")
        print(f"      - ProjectMemory.txt")
        print(f"      - TempMemory.txt")
        print(f"    - Intermediate/")
        print(f"      - AutoWritingHistory.txt")
        print(f"      - TodoHistory.txt")
        print(f"    - Output/")
        print(f"      - plaintext.txt")
        print(f"      - output.txt")
        
        return project_dir


def main():
    """Command-line interface for CreateNewProject."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python CreateNewProject.py <project_name>")
        print("\nExample:")
        print('  python CreateNewProject.py "MyResearchPaper"')
        sys.exit(1)
    
    project_name = sys.argv[1]
    
    creator = CreateNewProject()
    try:
        creator.create_project(project_name)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

