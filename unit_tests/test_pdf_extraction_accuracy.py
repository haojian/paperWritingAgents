#!/usr/bin/env python3
"""
Unit test for PDF extraction accuracy
Tests that AI-powered extraction of Introduction section from citesee.pdf
matches the expected content in citesee-intro.txt with at least 95% similarity.
"""

import unittest
import os
import sys
from pathlib import Path
from difflib import SequenceMatcher

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import PlainTextExtractor


class TestPDFExtractionAccuracy(unittest.TestCase):
    """Test PDF extraction accuracy against expected output."""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Find test files
        project_root = Path(__file__).parent.parent
        self.pdf_path = None
        self.expected_file = None
        
        # Try different possible locations (in order of preference)
        possible_pdf_paths = [
            project_root / "files" / "pdfs" / "citesee.pdf",
            project_root / "pdfs" / "citesee.pdf",
            project_root / "resources" / "citesee.pdf",
        ]
        
        possible_expected_paths = [
            project_root / "resources" / "unit-test-resources" / "citesee-intro.txt",
            project_root / "intermediate" / "citesee-intro.txt",
            project_root / "files" / "intermediate" / "citesee-intro.txt",
        ]
        
        for pdf_path in possible_pdf_paths:
            if pdf_path.exists():
                self.pdf_path = str(pdf_path)
                break
        
        for expected_path in possible_expected_paths:
            if expected_path.exists():
                self.expected_file = str(expected_path)
                break
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using SequenceMatcher.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize texts: lowercase, remove extra whitespace
        def normalize(text):
            # Remove extra whitespace and normalize
            text = ' '.join(text.split())
            return text.lower().strip()
        
        text1_norm = normalize(text1)
        text2_norm = normalize(text2)
        
        # Calculate similarity
        similarity = SequenceMatcher(None, text1_norm, text2_norm).ratio()
        return similarity
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
    def test_citesee_introduction_extraction_accuracy(self):
        """
        Test that AI-powered extraction of Introduction from citesee.pdf
        matches expected content with at least 95% similarity.
        """
        # Check if test files are available
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            self.skipTest(f"Test PDF not found: citesee.pdf")
        
        if not self.expected_file or not os.path.exists(self.expected_file):
            self.skipTest(f"Expected text file not found: citesee-intro.txt")
        
        # Initialize extractor with AI enabled
        extractor = PlainTextExtractor(
            gemini_api_key=self.api_key,
            use_ai=True
        )
        
        if not extractor.gemini_client:
            self.skipTest("Gemini API not available (API key may be invalid)")
        
        # Read expected content
        with open(self.expected_file, 'r', encoding='utf-8') as f:
            expected_text = f.read()
        
        # Extract Introduction section using AI
        try:
            extracted_text = extractor.extract_section(self.pdf_path, "INTRODUCTION")
        except Exception as e:
            self.fail(f"Failed to extract section: {e}")
        
        # Calculate similarity
        similarity = self._calculate_similarity(extracted_text, expected_text)
        
        # Assert similarity is at least 95%
        self.assertGreaterEqual(
            similarity,
            0.95,
            f"Extracted text similarity ({similarity:.2%}) is below 95% threshold.\n"
            f"Expected length: {len(expected_text)} chars\n"
            f"Extracted length: {len(extracted_text)} chars\n"
            f"Expected preview: {expected_text[:200]}...\n"
            f"Extracted preview: {extracted_text[:200]}..."
        )
        
        # Print success message with details
        print(f"\n✓ Extraction accuracy test passed!")
        print(f"  Similarity: {similarity:.2%}")
        print(f"  Expected length: {len(expected_text)} characters")
        print(f"  Extracted length: {len(extracted_text)} characters")
        print(f"  Difference: {abs(len(expected_text) - len(extracted_text))} characters")
    
    def test_similarity_calculation(self):
        """Test that similarity calculation works correctly."""
        # Test identical texts
        text1 = "This is a test sentence."
        text2 = "This is a test sentence."
        similarity = self._calculate_similarity(text1, text2)
        self.assertEqual(similarity, 1.0, "Identical texts should have 100% similarity")
        
        # Test very similar texts
        text1 = "This is a test sentence."
        text2 = "This is a test sentence!"
        similarity = self._calculate_similarity(text1, text2)
        self.assertGreater(similarity, 0.9, "Very similar texts should have high similarity")
        
        # Test different texts (completely unrelated)
        text1 = "This is a test sentence about testing."
        text2 = "The weather is sunny today with blue skies."
        similarity = self._calculate_similarity(text1, text2)
        self.assertLess(similarity, 0.5, "Completely different texts should have low similarity")


if __name__ == "__main__":
    unittest.main()

