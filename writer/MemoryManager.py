"""
Memory Manager
Manages three levels of memory:
- Global memory: Writing heuristics (from global_memory.txt)
- Single paper memory: Key ideas for the paper, potential paper reviews (from ProjectMemory.txt)
- Single paragraph memory: Templates, the paper (from TempMemory.txt for revisions)
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import re


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
        • Item 1
        • Item 2
        
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
                # Bullet point
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
        
        Args:
            project_memory_file: Path to ProjectMemory.txt
            
        Returns:
            Dictionary of project memory sections
        """
        project_memory_file = Path(project_memory_file)
        if not project_memory_file.exists():
            return {
                "Key Ideas": [],
                "Previous Content": [],
                "Outlines": []
            }
        
        with open(project_memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            return self._parse_memory_file(content)
    
    def load_temp_memory(self, temp_memory_file: str) -> Dict[str, List[str]]:
        """
        Load single paragraph memory from temp memory file (revision feedback).
        
        Args:
            temp_memory_file: Path to TempMemory.txt
            
        Returns:
            Dictionary of temp memory sections
        """
        temp_memory_file = Path(temp_memory_file)
        if not temp_memory_file.exists():
            return {"Revision Feedback": []}
        
        with open(temp_memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
            return self._parse_memory_file(content)
    
    def save_project_memory(self, project_memory_file: str, memory: Dict[str, List[str]]):
        """
        Save project memory to file.
        
        Args:
            project_memory_file: Path to ProjectMemory.txt
            memory: Dictionary of memory sections
        """
        project_memory_file = Path(project_memory_file)
        project_memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(project_memory_file, 'w', encoding='utf-8') as f:
            for section_name, items in memory.items():
                f.write(f"===== {section_name} =====\n")
                for item in items:
                    f.write(f"• {item}\n")
                f.write("\n")
    
    def save_temp_memory(self, temp_memory_file: str, memory: Dict[str, List[str]]):
        """
        Save temp memory to file.
        
        Args:
            temp_memory_file: Path to TempMemory.txt
            memory: Dictionary of memory sections
        """
        temp_memory_file = Path(temp_memory_file)
        temp_memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_memory_file, 'w', encoding='utf-8') as f:
            for section_name, items in memory.items():
                f.write(f"===== {section_name} =====\n")
                for item in items:
                    f.write(f"• {item}\n")
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

