#!/usr/bin/env python3
"""
Unit tests for Professor Feedback Agent
"""

import unittest
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from professor_feedback import ProfessorFeedbackAgent


class TestProfessorFeedbackAgent(unittest.TestCase):
    """Test cases for ProfessorFeedbackAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.skip_tests = not self.api_key
        
        if not self.skip_tests:
            self.professor = ProfessorFeedbackAgent(
                name="Test Professor",
                expertise="Academic Writing",
                api_provider="gemini",
                gemini_api_key=self.api_key
            )
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
    def test_generate_feedback_from_files(self):
        """Test generate_feedback_from_files method"""
        # Create test files
        heuristics_file = os.path.join(self.temp_dir, "heuristics.txt")
        history_file = os.path.join(self.temp_dir, "writing_history.txt")
        output_file = os.path.join(self.temp_dir, "todo_list.txt")
        
        # Write heuristics
        with open(heuristics_file, 'w') as f:
            f.write("1. Check for clarity\n2. Ensure proper structure\n3. Verify academic tone")
        
        # Write writing history
        with open(history_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("REVISION #1\n")
            f.write("Timestamp: 2024-01-01 00:00:00\n")
            f.write("Ideas File: ideas.txt\n")
            f.write("Template File: template.txt\n")
            f.write("=" * 80 + "\n\n")
            f.write("This is a test writing sample that needs feedback.")
        
        # Test generate_feedback_from_files
        result = self.professor.generate_feedback_from_files(
            heuristics_file_path=heuristics_file,
            writinghistory_file_path=history_file,
            output_file_path=output_file
        )
        
        # Assertions
        self.assertIn("todo_list", result)
        self.assertIn("latest_writing", result)
        self.assertIn("output_file", result)
        self.assertTrue(os.path.exists(output_file))
        self.assertGreater(len(result["todo_list"]), 0)
    
    def test_review_section(self):
        """Test review_section method"""
        professor = ProfessorFeedbackAgent(name="Test Professor")
        content = "This is a test introduction section for a research paper."
        feedback = professor.review_section("Introduction", content, "Test Topic")
        
        self.assertIsInstance(feedback, dict)
        self.assertIn("assessment", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("weaknesses", feedback)
        self.assertIn("recommendations", feedback)
    
    def test_review_paper(self):
        """Test review_paper method"""
        professor = ProfessorFeedbackAgent(name="Test Professor")
        paper = {
            "Introduction": "Introduction content here.",
            "Conclusion": "Conclusion content here."
        }
        feedback = professor.review_paper(paper, "Test Topic")
        
        self.assertIsInstance(feedback, dict)
        self.assertIn("overall_assessment", feedback)
        self.assertIn("strengths", feedback)
        self.assertIn("weaknesses", feedback)
        self.assertIn("section_feedback", feedback)
        self.assertIn("grade_estimate", feedback)


if __name__ == "__main__":
    unittest.main()

