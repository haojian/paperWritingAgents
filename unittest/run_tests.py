#!/usr/bin/env python3
"""
Test runner for Research Paper Writing Agents unit tests

Usage:
    python unittest/run_tests.py              # Run all tests
    python unittest/run_tests.py TestStudentWriterAgent  # Run specific test class
    python unittest/run_tests.py TestStudentWriterAgent.test_write_from_files  # Run specific test
"""

import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Discover and run tests
if __name__ == "__main__":
    # Get the directory containing this script (unittest folder)
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # Change to project root for consistent path resolution
    os.chdir(project_root)
    
    # Discover all test files
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(test_dir),
        pattern='test_*.py',
        top_level_dir=str(project_root)
    )
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

