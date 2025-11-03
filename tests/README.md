# Unit Tests

This directory contains unit tests for the Research Paper Writing Agents system.

## Running Tests

### Run all tests:
```bash
python tests/run_tests.py
```

### Run tests using unittest directly:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run tests using pytest (if installed):
```bash
pip install pytest
pytest tests/ -v
```

### Run a specific test class:
```bash
python -m unittest tests.test_student_writer.TestStudentWriterAgent -v
```

### Run a specific test method:
```bash
python -m unittest tests.test_student_writer.TestStudentWriterAgent.test_write_section -v
```

## Test Files

- `test_student_writer.py` - Tests for StudentWriterAgent
- `test_professor_feedback.py` - Tests for ProfessorFeedbackAgent
- `test_style_analyzer.py` - Tests for StyleAnalyzerAgent
- `test_pdf_extractor.py` - Tests for PDFSectionExtractorAgent
- `test_integration.py` - Integration tests for complete workflows

## Test Requirements

Some tests require API keys to run:
- Set `GEMINI_API_KEY` environment variable for AI-powered tests
- Set `OPENAI_API_KEY` for OpenAI-based tests

Tests that require API keys will be automatically skipped if the keys are not set.

## Example

```bash
# Set API key
export GEMINI_API_KEY="your_api_key_here"

# Run all tests
python tests/run_tests.py
```

