# Research Paper Writing Agents System

A multi-agent system for research paper writing with AI-powered style analysis and PDF section extraction.

## Overview

Four specialized agents work together:

1. **Student Writer Agent**: Drafts research paper content
2. **Style Analyzer Agent**: Analyzes style, structure, and writing quality using AI (Gemini/OpenAI)
3. **PDF Section Extractor Agent**: Extracts sections from PDF files
4. **Professor Feedback Agent**: Provides comprehensive academic feedback

## Architecture

```
Reference Papers → Style Analyzer → Template
                            ↓
                    Student Writer → Style Analyzer → Professor Feedback
```

## Features

- **AI-Powered Semantic Analysis**: Analyzes sentence/paragraph roles, transitions, and generates templates
- **PDF Section Extraction**: Extracts specific sections from PDFs using AI or rule-based methods
- **Multi-API Support**: Works with Gemini and OpenAI APIs
- **Reference Paper Learning**: Style Analyzer learns patterns from reference PDFs to create templates
- **Comprehensive Feedback**: Detailed style analysis and academic review

## Installation

```bash
pip install -r requirements.txt
```

**API Keys (Required for AI features):**
- **Gemini API**: 
  - Install: `pip install google-genai`
  - Get key: [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Set: `export GEMINI_API_KEY="your_key"`
- **OpenAI API**: Get key from [OpenAI Platform](https://platform.openai.com/api-keys)

## Quick Start

### Basic Usage

```python
from main import PaperWritingCoordinator

coordinator = PaperWritingCoordinator()
results = coordinator.write_and_review_paper(
    topic="Machine Learning Applications in Healthcare",
    sections=["Introduction", "Methodology", "Results", "Discussion", "Conclusion"],
    requirements={"length": "medium"},
    num_iterations=1
)
coordinator.print_detailed_report(results)
```

### With Reference Papers & AI

```python
from main import PaperWritingCoordinator
import os

coordinator = PaperWritingCoordinator(
    reference_papers=["paper1.pdf", "paper2.pdf"],
    gemini_api_key=os.getenv("GEMINI_API_KEY")
)

results = coordinator.write_and_review_paper(
    topic="Your Topic",
    sections=["Introduction", "Methodology", "Results"],
    num_iterations=1
)
```

### PDF Section Extraction

**Standalone Script:**
```bash
export GEMINI_API_KEY="your_key"
python extract_section.py "paper.pdf" "INTRODUCTION"
python extract_section.py "paper.pdf" "Introduction" "output.txt"  # Save to file
```

**Workflow: Extract section → Generate template:**
```bash
# Step 1: Extract section from PDF
python extract_section.py "paper.pdf" "INTRODUCTION" "intro.txt"

# Step 2: Analyze text file and generate template
python analyze_and_generate_template.py "intro.txt" "template.txt"
python analyze_and_generate_template.py "intro.txt" "template.txt" "Introduction"  # With section name
```

**Python API:**
```python
from agents import PDFSectionExtractorAgent
import os

extractor = PDFSectionExtractorAgent(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    use_ai=True  # Use AI for better accuracy
)

content = extractor.extract_section("paper.pdf", "Introduction")
```

**Note:** The three main agents (`StudentWriterAgent`, `StyleAnalyzerAgent`, `ProfessorFeedbackAgent`) are now top-level modules. You can import them directly:
```python
from student_writer import StudentWriterAgent
from style_analyzer import StyleAnalyzerAgent
from professor_feedback import ProfessorFeedbackAgent
```

Or for backward compatibility:
```python
from agents import StudentWriterAgent, StyleAnalyzerAgent, ProfessorFeedbackAgent
```

## API Reference

### Style Analyzer Agent

**Analyze text directly:**
```python
from style_analyzer import StyleAnalyzerAgent

analyzer = StyleAnalyzerAgent(
    api_provider="gemini",  # or "openai"
    gemini_api_key="your_key"
)

analysis = analyzer.analyze_section(section_text, section_name="Introduction")
# Returns: sentences, transitions, template, semantic_structure
```

**Analyze file and generate template file:**
```python
from style_analyzer import StyleAnalyzerAgent
import os

analyzer = StyleAnalyzerAgent(
    api_provider="gemini",
    gemini_api_key=os.getenv("GEMINI_API_KEY")
)

# Analyze a text file and save template to output file
result = analyzer.analyze_file_and_generate_template(
    input_file_path="input/citesee-intro.txt",
    output_file_path="output/template.txt",
    section_name="Introduction"  # Optional: will infer from filename
)

# Template is saved to output_file_path
# Result contains: sentences, transitions, template, semantic_structure
```

### PDF Section Extractor Agent

```python
from agents import PDFSectionExtractorAgent

extractor = PDFSectionExtractorAgent(use_ai=True, gemini_api_key="your_key")
content = extractor.extract_section(pdf_path, section_title)
```

**Supported formats**: "Introduction", "1. Introduction", "INTRODUCTION", "# Introduction"

### Other Agents

```python
from student_writer import StudentWriterAgent
from professor_feedback import ProfessorFeedbackAgent

writer = StudentWriterAgent()
content = writer.write_section("Introduction", "Topic")

professor = ProfessorFeedbackAgent(expertise="Computer Science")
feedback = professor.review_section("Introduction", content, "Topic")
```

## Running Examples

```bash
# Main paper writing system
python main.py

# Extract PDF section
python extract_section.py "resources/citesee.pdf" "INTRODUCTION"
```

## Output

The system generates:
- Paper content with all sections
- Style analysis (quality scores, metrics, issues, templates)
- Semantic role analysis (sentence/paragraph roles, transitions)
- Template compliance scores (when using reference papers)
- Professor feedback (assessment, grade estimate, suggestions)

## File Structure

```
research_paper_agents/
├── student_writer.py          # Student Writer Agent (top-level)
├── style_analyzer.py          # Style Analyzer Agent (top-level)
├── professor_feedback.py     # Professor Feedback Agent (top-level)
├── agents/
│   ├── __init__.py
│   └── pdf_section_extractor.py
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── run_tests.py          # Test runner
│   ├── test_student_writer.py
│   ├── test_professor_feedback.py
│   ├── test_style_analyzer.py
│   ├── test_pdf_extractor.py
│   └── test_integration.py
├── input/                     # Input resource folder
├── output/                    # Output resource folder
├── intermediate/              # Intermediate resource folder
├── resources/                 # PDF resources
├── main.py
├── extract_section.py
├── analyze_and_generate_template.py
├── write_from_template.py
├── generate_feedback.py
├── revise_from_todo.py
├── requirements.txt
└── README.md
```

## How Style Analyzer Learns from Reference Papers

1. Extracts text from PDF files
2. Analyzes writing patterns:
   - Sentence/paragraph semantic roles
   - Transition relationships
   - Structure and organization
3. Develops templates:
   - Role-based section templates
   - Expected role sequences
   - Role distribution patterns
4. Uses template for analysis:
   - Compares new papers against learned patterns
   - Identifies missing expected roles
   - Provides compliance scores and recommendations

## License

Open source for educational use.
