# Research Paper Writing Agents System

A multi-agent system for research paper writing with AI-powered style analysis and PDF section extraction.

> **Note:** See [NAMING_STYLE.md](NAMING_STYLE.md) for naming conventions and [DEVELOPMENT.md](DEVELOPMENT.md) for development instructions.

## Overview

This system provides tools and agents for:
1. **Extracting sections** from PDF papers
2. **Analyzing papers** to generate templates
3. **Writing papers** using memory-based approach
4. **Getting feedback** from professor agent

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
  - Set: `export OPENAI_API_KEY="your_key"`

## File Structure

```
research_paper_agents/
├── pdfs/                        # Example paper PDF files
├── extracted_sections/          # Extracted section text files
│   └── [paper_name]/            # Each paper has a subdirectory
│       ├── 1_abstract.txt
│       ├── 2_introduction.txt
│       └── ...
├── paper_analysis/              # Paper annotation files
├── projects/                    # Project data
│   └── [project_name]/          # Each project has a subdirectory
│       ├── Memory/
│       │   ├── ProjectMemory.txt
│       │   └── TempMemory.txt
│       ├── Intermediate/
│       │   ├── AutoWritingHistory.txt
│       │   └── TodoHistory.txt
│       └── Output/
│           ├── plaintext.txt
│           └── output.txt
├── global_memory.txt            # Global memory file (writing heuristics)
├── tools/                       # Tool modules
│   ├── CloudAIWrapper.py       # Unified AI wrapper (Gemini/OpenAI)
│   ├── PlainTextExtractor.py   # Extract all sections from PDF
│   ├── PaperAnalyzer.py        # Analyze papers and generate templates
│   ├── ProjectCreator.py       # Create new project structure
│   └── Professor.py            # Generate to-do lists from global memory
├── agents/                     # Agent modules
│   └── Writer.py               # Writer agent with multiple modes
├── student_writer.py           # Student Writer Agent
├── style_analyzer.py           # Style Analyzer Agent
├── professor_feedback.py       # Professor Feedback Agent
├── unit_tests/                 # Unit tests
└── README.md
```

## Usage

### 1. Extract Sections from PDF

Extract all sections from a PDF file and save them as text files:

```bash
python -m tools.PlainTextExtractor paper.pdf --paper-name "MyPaper"
```

Or use the class directly:
```python
from tools import PlainTextExtractor

extractor = PlainTextExtractor()
extractor.extract_all_sections("paper.pdf", paper_name="MyPaper")
```

### 2. Analyze Paper and Generate Templates

Analyze a text file and generate template annotations:

```bash
python -m tools.PaperAnalyzer intro.txt --section-name "Introduction" --paper-name "MyPaper"
```

Or use the class:
```python
from tools import PaperAnalyzer

analyzer = PaperAnalyzer()
result = analyzer.analyze_file("intro.txt", section_name="Introduction", paper_name="MyPaper")
```

### 3. Create New Project

Create a new project with the required folder structure:

```bash
# Using command-line interface
python -m tools.ProjectCreator "MyResearchProject"

# Or directly run the script
python tools/ProjectCreator.py "MyResearchProject"
```

**What it creates:**
- `projects/MyResearchProject/` - Main project directory
  - `Memory/` - Stores project-specific memory
    - `ProjectMemory.txt` - Key ideas, previous content, and outlines
    - `TempMemory.txt` - Temporary revision feedback
  - `Intermediate/` - Intermediate files
    - `AutoWritingHistory.txt` - Writing history log
    - `TodoHistory.txt` - Todo list history
  - `Output/` - Output files
    - `plaintext.txt` - Plain text output
    - `output.txt` - Final output

**Using the class directly:**
```python
from tools import ProjectCreator

# Create with default projects directory
creator = ProjectCreator()
project_dir = creator.create_project("MyResearchProject")

# Create with custom projects directory
creator = ProjectCreator(projects_base_dir="custom_projects")
project_dir = creator.create_project("MyResearchProject")
```

**Note:** The script will create the project structure if it doesn't exist, but won't overwrite existing files.

### 4. Write Using Memory

#### NewParagraph Mode

Write new paragraphs using project memory:

```python
from agents import Writer

writer = Writer(project_path="projects/MyProject")
result = writer.new_paragraph()
# Returns: {'plain_text': ..., 'latex': ...}
```

#### ReviseParagraph Mode

Revise existing paragraphs based on feedback:

```python
writer = Writer(project_path="projects/MyProject")
result = writer.revise_paragraph()
# Returns: {'plain_text': ..., 'latex': ..., 'version': 1}
# Saves to WritingHistory.txt with version number
```

**TempMemory.txt should contain:**
- Current Paragraph: The paragraph to revise
- Revision Feedback: Feedback on what needs to be changed
- Topic Sentence: (Optional) Topic sentence to incorporate
- Bullet Points: (Optional) Bullet points to expand on
- Template Flow: (Optional) Template describing the logic flow

#### Using Command Line

```bash
# NewParagraph mode
python -m agents.Writer projects/MyProject --mode newparagraph

# ReviseParagraph mode
python -m agents.Writer projects/MyProject --mode reviseparagraph
```

Ask professor for review:
```python
todo_list = writer.ask_professor_review()
```

Revise based on todo list (legacy method):
```python
revised = writer.revise_from_todo()
```

### 5. Memory Format

Memory files use human-readable bullet format:

```
===== Key Ideas =====
• Main idea 1
• Main idea 2

===== Previous Content =====
• Previous paragraph content

===== Outlines =====
• Outline point 1
• Outline point 2

===== Revision Feedback =====
• Improve clarity
• Add more details
```

### 6. Global Memory

Edit `global_memory.txt` to set writing heuristics:

```
===== Writing Heuristics =====
• Clarity: Ensure ideas are clearly expressed
• Structure: Follow logical flow
• Academic Tone: Maintain formal academic style
• Evidence: Support claims with evidence
• Coherence: Ensure smooth transitions
```

## Memory Levels

The system uses three levels of memory:

1. **Global Memory** (`global_memory.txt`): Writing heuristics applicable to all papers
2. **Project Memory** (`projects/[project]/Memory/ProjectMemory.txt`): Key ideas, previous content, outlines for a specific paper
3. **Temp Memory** (`projects/[project]/Memory/TempMemory.txt`): Revision feedback for current paragraph

## Writer Modes

### Paragraph Writing Mode

The Writer supports paragraph-writing mode where:
- Input: Project memory, paragraph templates (optional), TempMemory.txt (revision feedback)
- Output: Generated paragraph text
- Can ask professor to review and get todo list
- Can revise based on todo list

Example:
```python
writer = Writer(project_path="projects/MyProject")

# Write with template
paragraph = writer.write_paragraph(paragraph_template="[brief introduction]...")

# Get review
todo_list = writer.ask_professor_review()

# Revise
revised = writer.revise_from_todo()
```

## API Reference

### CloudAIWrapper

Unified wrapper for Gemini and OpenAI:

```python
from tools import CloudAIWrapper

ai = CloudAIWrapper(provider="gemini")  # or "openai"
text = ai.generate("Write a paragraph about...")
```

### MemoryManager

Manage three levels of memory:

```python
from tools import MemoryManager

mm = MemoryManager()
global_mem = mm.get_global_memory()
project_mem = mm.load_project_memory("projects/MyProject/Memory/ProjectMemory.txt")
temp_mem = mm.load_temp_memory("projects/MyProject/Memory/TempMemory.txt")
```

### Professor

Generate to-do lists from global memory:

```python
from tools import Professor

prof = Professor()
todo_list = prof.generate_todo_list("writing_history.txt")
```

## Testing

Run unit tests:

```bash
python -m unittest discover -s unit_tests -p "test_*.py" -v
```

Or use the test runner:

```bash
python unit_tests/run_tests.py
```

## Workflow Example

1. **Extract sections from PDF:**
   ```bash
   python -m tools.PlainTextExtractor paper.pdf --paper-name "ExamplePaper"
   ```

2. **Analyze extracted introduction:**
   ```bash
   python -m tools.PaperAnalyzer extracted_sections/ExamplePaper/2_introduction.txt --section-name "Introduction"
   ```

3. **Create a new project:**
   ```bash
   python -m tools.ProjectCreator "MyPaper"
   ```

4. **Edit project memory:**
   - Edit `projects/MyPaper/Memory/ProjectMemory.txt` with key ideas

5. **Write paragraphs:**
   ```python
   from agents import Writer
   writer = Writer("projects/MyPaper")
   
   # NewParagraph mode
   result = writer.new_paragraph()
   
   # Or ReviseParagraph mode (requires Current Paragraph and Revision Feedback in TempMemory.txt)
   result = writer.revise_paragraph()
   print(f"Version {result['version']} saved")
   ```

6. **Get feedback:**
   ```python
   todo_list = writer.ask_professor_review()
   ```

7. **Revise:**
   ```python
   revised = writer.revise_from_todo()
   ```
