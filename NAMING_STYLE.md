# Naming Style Guide

This document defines the naming conventions used throughout the Research Paper Writing Agents project.

## Overview

The project follows Python naming conventions (PEP 8) with consistent lowercase-with-underscores style for directories and files.

## Directory Names

**Rule:** Use lowercase letters with underscores (snake_case)

**Examples:**
```
✓ tools/
✓ extracted_sections/
✓ paper_analysis/
✓ projects/
✓ agents/
✓ unit_tests/
✓ pdfs/
```

**Avoid:**
```
✗ Utilities/
✗ Extracted-sections/
✗ PaperAnalysis/
✗ Projects/
✗ Writer/
```

## File Names

**Rule:** Use lowercase letters with underscores (snake_case)

**Examples:**
```
✓ extract_sections.py
✓ memory_manager.py
✓ cloud_ai_wrapper.py
✓ paper_analyzer.py
✓ create_new_project.py
```

**Special cases:**
- Configuration files: `global_memory.txt`, `requirements.txt`
- README files: `README.md` (capitalized as per convention)

**Avoid:**
```
✗ PlainTextExtractor.py
✗ MemoryManager.py
✗ CloudAIWrapper.py
```

## Python Module Names

**Rule:** Match directory/file names (lowercase with underscores)

**Examples:**
```python
# Module imports
from tools import PlainTextExtractor
from tools import MemoryManager
from agents import Writer
from tools.CloudAIWrapper import CloudAIWrapper
```

## Class Names

**Rule:** Use PascalCase (UpperCamelCase)

**Examples:**
```python
class PlainTextExtractor:
    pass

class MemoryManager:
    pass

class CloudAIWrapper:
    pass

class StudentWriterAgent:
    pass
```

**Avoid:**
```
✗ class extract_sections:
✗ class memoryManager:
✗ class cloudAIWrapper:
```

## Method and Function Names

**Rule:** Use lowercase with underscores (snake_case)

**Examples:**
```python
def extract_all_sections():
    pass

def load_project_memory():
    pass

def generate_todo_list():
    pass

def write_paragraph():
    pass
```

**Avoid:**
```
✗ def extractAllSections():
✗ def LoadProjectMemory():
✗ def generateTodoList():
```

## Variable Names

**Rule:** Use lowercase with underscores (snake_case)

**Examples:**
```python
output_base_dir = "extracted_sections"
project_memory_file = "projects/MyProject/Memory/ProjectMemory.txt"
temp_memory_file = "projects/MyProject/Memory/TempMemory.txt"
writing_history = []
```

**Avoid:**
```
✗ outputBaseDir
✗ projectMemoryFile
✗ WritingHistory
```

## Constants

**Rule:** Use UPPERCASE with underscores

**Examples:**
```python
GEMINI_AVAILABLE = True
PDFPLUMBER_AVAILABLE = True
DEFAULT_OUTPUT_DIR = "extracted_sections"
MAX_TEXT_LENGTH = 150000
```

**Avoid:**
```
✗ geminiAvailable
✗ defaultOutputDir
```

## Private Methods and Variables

**Rule:** Prefix with single underscore

**Examples:**
```python
def _extract_section_with_ai():
    pass

def _load_global_memory():
    pass

def _parse_memory_file():
    pass

self._available = False
self._temp_dir = None
```

## Package/Module Imports

**Rule:** Use lowercase module names

**Examples:**
```python
from tools import PlainTextExtractor
from tools import MemoryManager
from tools.CloudAIWrapper import CloudAIWrapper
from agents import Writer
```

**Avoid:**
```
✗ from Tools import PlainTextExtractor
✗ from Writer import MemoryManager
```

## Project Structure Subdirectories

**Note:** Subdirectories within projects keep their capitalized names as they represent the internal project structure:

```
projects/
└── [project_name]/
    ├── Memory/     # Kept capitalized (project structure)
    ├── Intermediate/       # Kept capitalized (project structure)
    └── Output/            # Kept capitalized (project structure)
```

These are intentional and match the project specification.

## Summary Table

| Item | Convention | Example |
|------|-----------|---------|
| Directory names | `lowercase_with_underscores` | `tools/`, `extracted_sections/` |
| File names | `lowercase_with_underscores` | `extract_sections.py`, `memory_manager.py` |
| Module names | `lowercase_with_underscores` | `tools`, `writer` |
| Class names | `PascalCase` | `PlainTextExtractor`, `MemoryManager` |
| Method/Function names | `lowercase_with_underscores` | `extract_all_sections()`, `load_project_memory()` |
| Variable names | `lowercase_with_underscores` | `output_base_dir`, `project_memory_file` |
| Constants | `UPPERCASE_WITH_UNDERSCORES` | `GEMINI_AVAILABLE`, `MAX_TEXT_LENGTH` |
| Private methods/variables | `_lowercase_with_underscores` | `_extract_section_with_ai()`, `_temp_dir` |

## Best Practices

1. **Be consistent:** Once you choose a naming style, use it consistently throughout the project.
2. **Be descriptive:** Names should clearly indicate their purpose.
3. **Avoid abbreviations:** Use full words when possible (e.g., `extract_sections` not `ext_sec`).
4. **Use verbs for functions:** Function names should be verbs (e.g., `extract`, `load`, `generate`).
5. **Use nouns for classes:** Class names should be nouns (e.g., `PlainTextExtractor`, `MemoryManager`).

## Examples from the Codebase

### Good Examples

```python
# Directory structure
tools/
agents/
extracted_sections/

# Class definition
class PlainTextExtractor:
    def __init__(self, output_base_dir: str = "extracted_sections"):
        self.output_base_dir = Path(output_base_dir)
    
    def extract_all_sections(self, pdf_path: str):
        section_content = self._extract_section_with_ai(text, section_title)
        return section_content
```

### Avoid

```python
# Bad directory names
Utilities/
Extracted-sections/
PaperAnalysis/

# Bad class names
class extractSections:
class memory_manager:

# Bad method names
def ExtractAllSections():
def loadProjectMemory():
```

## References

- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

