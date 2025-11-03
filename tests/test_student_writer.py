#!/usr/bin/env python3
"""
Unit tests for Student Writer Agent
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from student_writer import StudentWriterAgent


class TestStudentWriterAgent(unittest.TestCase):
    """Test cases for StudentWriterAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.skip_tests = not self.api_key
        
        if not self.skip_tests:
            self.writer = StudentWriterAgent(
                name="Test Student Writer",
                api_provider="gemini",
                gemini_api_key=self.api_key
            )
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
    def test_write_from_files(self):
        """Test write_from_files method"""
        # Create test files
        ideas_file = os.path.join(self.temp_dir, "ideas.txt")
        template_file = os.path.join(self.temp_dir, "template.txt")
        output_file = os.path.join(self.temp_dir, "writing_history.txt")
        
        with open(ideas_file, 'w') as f:
            f.write("Main idea: Test AI writing system\nKey points: Testing and validation")
        
        with open(template_file, 'w') as f:
            f.write("[brief introduction of the background]. [explains why the problem is important]")
        
        # Test write_from_files
        result = self.writer.write_from_files(
            ideas_file_path=ideas_file,
            template_file_path=template_file,
            output_file_path=output_file
        )
        
        # Assertions
        self.assertIn("generated_text", result)
        self.assertIn("output_file", result)
        self.assertIn("timestamp", result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(len(result["generated_text"]), 0)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
    def test_revise_from_todo_list(self):
        """Test revise_from_todo_list method"""
        # Create test files
        todo_file = os.path.join(self.temp_dir, "todo_list.txt")
        history_file = os.path.join(self.temp_dir, "writing_history.txt")
        ideas_file = os.path.join(self.temp_dir, "ideas.txt")
        template_file = os.path.join(self.temp_dir, "template.txt")
        
        # Write initial writing history
        with open(history_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("REVISION #1\n")
            f.write("Timestamp: 2024-01-01 00:00:00\n")
            f.write("Ideas File: ideas.txt\n")
            f.write("Template File: template.txt\n")
            f.write("=" * 80 + "\n\n")
            f.write("This is the initial writing that needs to be revised.")
        
        # Write todo list
        with open(todo_file, 'w') as f:
            f.write("1. Improve clarity\n2. Add more details\n3. Fix grammar")
        
        with open(ideas_file, 'w') as f:
            f.write("Main idea: Test revision")
        
        with open(template_file, 'w') as f:
            f.write("[brief introduction]")
        
        # Test revise_from_todo_list
        result = self.writer.revise_from_todo_list(
            todo_list_file_path=todo_file,
            writinghistory_file_path=history_file,
            ideas_file_path=ideas_file,
            template_file_path=template_file
        )
        
        # Assertions
        self.assertIn("revised_text", result)
        self.assertIn("original_writing", result)
        self.assertGreater(len(result["revised_text"]), 0)
    
    def test_write_section(self):
        """Test write_section method (basic functionality)"""
        # This test works even without API key (uses template-based generation)
        writer = StudentWriterAgent(name="Test Writer")
        content = writer.write_section("Introduction", "Test Topic")
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 0)
        self.assertIn("Test Topic", content)
    
    def test_write_full_paper(self):
        """Test write_full_paper method"""
        writer = StudentWriterAgent(name="Test Writer")
        paper = writer.write_full_paper(
            topic="Test Topic",
            sections=["Introduction", "Conclusion"]
        )
        self.assertIsInstance(paper, dict)
        self.assertEqual(len(paper), 2)
        self.assertIn("Introduction", paper)
        self.assertIn("Conclusion", paper)


if __name__ == "__main__":
    unittest.main()

