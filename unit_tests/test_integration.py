#!/usr/bin/env python3
"""
Integration tests for the complete workflow
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
from style_analyzer import StyleAnalyzerAgent
from professor_feedback import ProfessorFeedbackAgent


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for the complete paper writing workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.skip_tests = not self.api_key
        
        if not self.skip_tests:
            self.writer = StudentWriterAgent(
                name="Test Writer",
                api_provider="gemini",
                gemini_api_key=self.api_key
            )
            self.analyzer = StyleAnalyzerAgent(
                name="Test Analyzer",
                api_provider="gemini",
                gemini_api_key=self.api_key
            )
            self.professor = ProfessorFeedbackAgent(
                name="Test Professor",
                api_provider="gemini",
                gemini_api_key=self.api_key
            )
        
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
    def test_complete_workflow(self):
        """Test the complete workflow: write -> analyze -> feedback"""
        # Step 1: Generate initial writing
        ideas_file = os.path.join(self.temp_dir, "ideas.txt")
        template_file = os.path.join(self.temp_dir, "template.txt")
        writing_history_file = os.path.join(self.temp_dir, "writing_history.txt")
        
        with open(ideas_file, 'w') as f:
            f.write("Main idea: Test integration workflow\nKey concepts: Testing, Integration, Validation")
        
        with open(template_file, 'w') as f:
            f.write("[brief introduction of the background]. [explains why the problem is important]")
        
        # Generate writing
        write_result = self.writer.write_from_files(
            ideas_file_path=ideas_file,
            template_file_path=template_file,
            output_file_path=writing_history_file
        )
        self.assertIn("generated_text", write_result)
        
        # Step 2: Analyze the writing
        analyze_result = self.analyzer.analyze_file_and_generate_template(
            input_file_path=writing_history_file,
            output_file_path=os.path.join(self.temp_dir, "analysis_template.txt"),
            section_name="Introduction"
        )
        self.assertIn("template", analyze_result)
        
        # Step 3: Generate feedback
        heuristics_file = os.path.join(self.temp_dir, "heuristics.txt")
        todo_file = os.path.join(self.temp_dir, "todo_list.txt")
        
        with open(heuristics_file, 'w') as f:
            f.write("1. Check clarity\n2. Verify structure\n3. Ensure completeness")
        
        feedback_result = self.professor.generate_feedback_from_files(
            heuristics_file_path=heuristics_file,
            writinghistory_file_path=writing_history_file,
            output_file_path=todo_file
        )
        self.assertIn("todo_list", feedback_result)
        
        # Step 4: Revise based on feedback
        revise_result = self.writer.revise_from_todo_list(
            todo_list_file_path=todo_file,
            writinghistory_file_path=writing_history_file,
            ideas_file_path=ideas_file,
            template_file_path=template_file
        )
        self.assertIn("revised_text", revise_result)
        
        # Verify the complete workflow completed successfully
        self.assertTrue(os.path.exists(writing_history_file))
        self.assertTrue(os.path.exists(todo_file))


if __name__ == "__main__":
    unittest.main()

