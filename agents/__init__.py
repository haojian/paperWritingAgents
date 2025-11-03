"""Research Paper Writing Agents Package."""

# Import from root-level modules (for backward compatibility)
import sys
import os

# Add parent directory to path if needed for importing root-level modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from student_writer import StudentWriterAgent
from style_analyzer import StyleAnalyzerAgent
from professor_feedback import ProfessorFeedbackAgent
from .pdf_section_extractor import PDFSectionExtractorAgent

__all__ = [
    'StudentWriterAgent', 
    'StyleAnalyzerAgent', 
    'ProfessorFeedbackAgent',
    'PDFSectionExtractorAgent'
]

