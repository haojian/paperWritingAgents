# Development Instructions

Quick reference for developers working on the Research Paper Writing Agents project.

## Running Unit Tests

### Run All Tests

```bash
# Using the test runner
python unit_tests/run_tests.py

# Using unittest directly
python -m unittest discover -s unit_tests -p "test_*.py" -v
```

### Run Specific Tests

```bash
# Run a specific test file
python -m unittest unit_tests.test_pdf_extraction_accuracy -v

# Run a specific test method
python -m unittest unit_tests.test_pdf_extraction_accuracy.TestPDFExtractionAccuracy.test_similarity_calculation -v
```

### API Keys Required

Some tests require API keys. Set them before running:

```bash
export GEMINI_API_KEY="your_api_key_here"
python unit_tests/run_tests.py
```

Tests that require API keys will be automatically skipped if keys are not set.

## Writing New Tests

### Test File Template

Create test files in `unit_tests/` following the naming: `test_<module_name>.py`

```python
#!/usr/bin/env python3
import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from <module> import <Class>


class Test<ClassName>(unittest.TestCase):
    """Test cases for <ClassName>"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = os.getenv("GEMINI_API_KEY")
    
    @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
    def test_feature(self):
        """Test description"""
        # Test implementation
        self.assertEqual(expected, actual)
```

### Test Best Practices

1. **Skip tests when prerequisites are missing**:
   ```python
   @unittest.skipIf(not os.getenv("GEMINI_API_KEY"), "GEMINI_API_KEY not set")
   ```

2. **Provide helpful error messages**:
   ```python
   self.assertGreaterEqual(similarity, 0.95, f"Similarity ({similarity:.2%}) is below threshold")
   ```

3. **Use setUp/tearDown for common setup/cleanup**

## Development Setup

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys (required for AI features)
export GEMINI_API_KEY="your_key"
# or
export OPENAI_API_KEY="your_key"
```

### Code Style

See [NAMING_STYLE.md](NAMING_STYLE.md) for naming conventions.

**Quick reference:**
- Directories: `lowercase_with_underscores` (e.g., `tools/`)
- Files: `lowercase_with_underscores.py` (e.g., `extract_sections.py`)
- Classes: `PascalCase` (e.g., `PlainTextExtractor`)
- Functions: `lowercase_with_underscores()` (e.g., `extract_all_sections()`)
- Variables: `lowercase_with_underscores` (e.g., `output_base_dir`)

## Updating Project Memory

### Update Memory from StagedOutput.txt

Summarize the content in `StagedOutput.txt` and update the "Previous Content" section in `ProjectMemory.txt`:

```bash
# Update memory for a project (using project name)
python -m tools.MemoryManager privacypowder

# Or using direct file call
python tools/MemoryManager.py privacypowder

# Or using full path
python -m tools.MemoryManager projects/privacypowder

# Specify AI provider
python -m tools.MemoryManager privacypowder --provider gemini
python -m tools.MemoryManager privacypowder --provider openai
```

**What it does:**
- Reads `projects/<project>/Output/StagedOutput.txt`
- Uses AI to extract 10 diverse, important sentences
- Updates `projects/<project>/Memory/ProjectMemory.txt` "Previous Content" section
- Requires `GEMINI_API_KEY` or `OPENAI_API_KEY` environment variable

## Project Structure

```
tools/         # Tool modules
agents/        # Agent modules (Writer, PDFSectionExtractor, etc.)
unit_tests/    # Unit tests
```

See [README.md](README.md) for complete structure.
