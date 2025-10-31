"""
Student Writer Agent
Generates research paper content based on topics and requirements.
Uses AI APIs to generate text based on ideas and templates.
"""

from typing import Dict, List, Optional, Tuple
from collections import Counter
import json
import os
import re
from datetime import datetime

# Try to import Google Gen AI SDK
try:
    from google.genai import Client as GenAIClient
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import OpenAI API
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class StudentWriterAgent:
    """Agent that acts as a student writing a research paper."""
    
    def __init__(self, name: str = "Student Writer",
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Student Writer Agent.
        
        Args:
            name: Name of the agent
            api_provider: AI API provider to use ("gemini" or "openai")
            gemini_api_key: Optional Gemini API key. If not provided, will try GEMINI_API_KEY env variable.
            openai_api_key: Optional OpenAI API key. If not provided, will try OPENAI_API_KEY env variable.
        """
        self.name = name
        self.draft_history = []
        self.api_provider = api_provider.lower()
        
        # Setup API based on provider
        self.api_model = None
        self.api_available = False
        
        if self.api_provider == "gemini":
            self._setup_gemini(gemini_api_key)
        elif self.api_provider == "openai":
            self._setup_openai(openai_api_key)
        else:
            print(f"Warning: Unknown API provider '{api_provider}'. Supported: 'gemini', 'openai'")
    
    def _setup_gemini(self, api_key: Optional[str] = None):
        """Setup Google Gen AI SDK (new Gemini API)."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not GEMINI_AVAILABLE:
            print("Warning: google-genai not installed. Install with: pip install google-genai")
            return
        
        if not self.api_key:
            print("Note: No Gemini API key provided. Set GEMINI_API_KEY environment variable or pass gemini_api_key parameter.")
            return
        
        try:
            self.api_model = GenAIClient(api_key=self.api_key)
            self.api_available = True
            print(f"✓ Google Gen AI SDK configured for text generation")
        except Exception as e:
            print(f"Warning: Failed to configure Google Gen AI SDK: {str(e)}")
            self.api_available = False
    
    def _setup_openai(self, api_key: Optional[str] = None):
        """Setup OpenAI API."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not OPENAI_AVAILABLE:
            print("Warning: openai not installed. Install with: pip install openai")
            return
        
        if not self.api_key:
            print("Note: No OpenAI API key provided. Set OPENAI_API_KEY environment variable or pass openai_api_key parameter.")
            return
        
        try:
            self.api_model = openai.OpenAI(api_key=self.api_key)
            self.api_available = True
            print(f"✓ OpenAI API configured for text generation")
        except Exception as e:
            print(f"Warning: Failed to configure OpenAI API: {str(e)}")
            self.api_available = False
    
    def write_section(self, section_name: str, topic: str, requirements: Optional[Dict] = None) -> str:
        """
        Write a section of the research paper.
        
        Args:
            section_name: Name of the section (e.g., "Introduction", "Methodology")
            topic: The research topic
            requirements: Optional requirements dictionary
            
        Returns:
            The written section content
        """
        if requirements is None:
            requirements = {}
        
        # Generate content based on section type
        if section_name.lower() == "introduction":
            content = self._write_introduction(topic, requirements)
        elif section_name.lower() == "methodology":
            content = self._write_methodology(topic, requirements)
        elif section_name.lower() == "results":
            content = self._write_results(topic, requirements)
        elif section_name.lower() == "discussion":
            content = self._write_discussion(topic, requirements)
        elif section_name.lower() == "conclusion":
            content = self._write_conclusion(topic, requirements)
        else:
            content = self._write_generic_section(section_name, topic, requirements)
        
        # Record draft
        draft_entry = {
            "section": section_name,
            "content": content,
            "topic": topic
        }
        self.draft_history.append(draft_entry)
        
        return content
    
    def write_full_paper(self, topic: str, sections: List[str], requirements: Optional[Dict] = None) -> Dict[str, str]:
        """
        Write a complete research paper.
        
        Args:
            topic: The research topic
            sections: List of section names to write
            requirements: Optional requirements dictionary
            
        Returns:
            Dictionary mapping section names to their content
        """
        if requirements is None:
            requirements = {}
        
        paper = {}
        for section in sections:
            paper[section] = self.write_section(section, topic, requirements)
        
        return paper
    
    def _write_introduction(self, topic: str, requirements: Dict) -> str:
        """Generate introduction section."""
        length = requirements.get("length", "medium")
        
        intro = f"""# Introduction

This paper investigates {topic}. The importance of this research area stems from its significant implications for both theoretical understanding and practical applications. 

Previous research in this field has established foundational knowledge, yet several gaps remain in our current understanding. This study aims to address these gaps by examining {topic} from multiple perspectives.

The objectives of this research are: (1) to analyze the key aspects of {topic}, (2) to identify patterns and relationships, and (3) to contribute novel insights to the existing body of knowledge. This research contributes to the field by providing a comprehensive analysis and novel findings.

The paper is organized as follows: Section 2 reviews relevant literature, Section 3 describes the methodology, Section 4 presents the results, Section 5 discusses the findings, and Section 6 concludes with implications and future directions."""
        
        return intro
    
    def _write_methodology(self, topic: str, requirements: Dict) -> str:
        """Generate methodology section."""
        methodology = f"""# Methodology

This section outlines the research approach employed in this study. The methodology is designed to ensure rigor and reliability in investigating {topic}.

## Research Design

A comprehensive research design was adopted to address the research questions. This design incorporates both qualitative and quantitative elements to provide a holistic understanding of the phenomenon under investigation.

## Data Collection

Data collection procedures were established to gather relevant information. The sources of data include primary sources such as experiments, surveys, or direct observations, as well as secondary sources including academic literature and existing datasets.

## Analysis Methods

The analytical framework employs appropriate statistical and analytical techniques to examine the data. These methods are selected to align with the research objectives and the nature of the data collected."""
        
        return methodology
    
    def _write_results(self, topic: str, requirements: Dict) -> str:
        """Generate results section."""
        results = f"""# Results

This section presents the findings from the investigation of {topic}. The results are organized to clearly communicate the key discoveries and patterns identified through the research process.

## Key Findings

The analysis revealed several important findings. First, significant patterns were observed that contribute to our understanding of {topic}. Second, the data indicates relationships between various factors that merit further investigation.

## Statistical Analysis

Statistical tests were conducted to validate the findings. The results demonstrate statistical significance in key areas, supporting the main conclusions of this research.

## Data Visualization

[Tables and figures would be included here to illustrate the findings]"""
        
        return results
    
    def _write_discussion(self, topic: str, requirements: Dict) -> str:
        """Generate discussion section."""
        discussion = f"""# Discussion

This section interprets the findings in the context of existing literature and theoretical frameworks. The results obtained from studying {topic} provide insights that both confirm and extend previous research.

## Interpretation of Findings

The findings suggest that {topic} exhibits characteristics that align with theoretical predictions, while also revealing unexpected patterns that require further investigation. These results contribute to a more nuanced understanding of the phenomenon.

## Comparison with Previous Research

When compared to previous studies, our findings both corroborate existing knowledge and introduce new perspectives. The convergence with established research provides confidence in our methodology, while the novel aspects highlight areas for future exploration.

## Implications

The implications of these findings extend to both theoretical understanding and practical applications. Theoretically, this research advances our conceptual framework. Practically, the findings may inform decision-making processes and guide future interventions."""
        
        return discussion
    
    def _write_conclusion(self, topic: str, requirements: Dict) -> str:
        """Generate conclusion section."""
        conclusion = f"""# Conclusion

This research has investigated {topic} through a comprehensive approach. The study has achieved its primary objectives and contributed meaningful insights to the field.

## Summary of Contributions

The main contributions of this work include: (1) a detailed analysis of {topic}, (2) identification of key patterns and relationships, and (3) theoretical and practical implications that extend current knowledge.

## Limitations

It is important to acknowledge the limitations of this study. These include constraints related to sample size, data collection methods, and the scope of investigation. Future research should address these limitations to further advance understanding.

## Future Directions

Several promising directions for future research emerge from this work. These include longitudinal studies, expanded sample sizes, and investigations into related phenomena that could build upon these findings."""
        
        return conclusion
    
    def _write_generic_section(self, section_name: str, topic: str, requirements: Dict) -> str:
        """Generate a generic section."""
        return f"""# {section_name}

This section addresses {section_name.lower()} aspects of {topic}. The content here is developed to provide comprehensive coverage of relevant information related to the research topic.

[Student draft content for {section_name}]"""
    
    def revise_section(self, section_name: str, original_content: str, feedback: str) -> str:
        """
        Revise a section based on feedback.
        
        Args:
            section_name: Name of the section
            original_content: Original section content
            feedback: Feedback to incorporate
            
        Returns:
            Revised section content
        """
        revised = f"""{original_content}

## Revised Section (Based on Feedback)

{original_content}

Note: The following revisions were made based on feedback: {feedback[:200]}... The section has been improved to address the comments received."""
        
        return revised
    
    def write_from_files(self, ideas_file_path: str, template_file_path: str, output_file_path: str) -> Dict:
        """
        Generate text based on ideas and template files, saving results with revision history.
        
        Args:
            ideas_file_path: Path to text file containing main ideas
            template_file_path: Path to text file containing template information
            output_file_path: Path to output file that stores writing results with revision history
                              (latest results at the top)
        
        Returns:
            Dictionary containing:
            - generated_text: The generated text content
            - ideas_file: Path to input ideas file
            - template_file: Path to input template file
            - output_file: Path to output file
            - timestamp: Timestamp of generation
        """
        if not self.api_available:
            raise ValueError(
                f"API ({self.api_provider}) is not available. "
                "Please configure the API key or install the required library."
            )
        
        # Check if input files exist
        if not os.path.exists(ideas_file_path):
            raise FileNotFoundError(f"Ideas file not found: {ideas_file_path}")
        if not os.path.exists(template_file_path):
            raise FileNotFoundError(f"Template file not found: {template_file_path}")
        
        # Read ideas file
        try:
            with open(ideas_file_path, 'r', encoding='utf-8') as f:
                ideas_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read ideas file '{ideas_file_path}': {str(e)}")
        
        if not ideas_content.strip():
            raise ValueError(f"Ideas file '{ideas_file_path}' is empty")
        
        # Read template file
        try:
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read template file '{template_file_path}': {str(e)}")
        
        if not template_content.strip():
            raise ValueError(f"Template file '{template_file_path}' is empty")
        
        # Generate text using AI API with validation and feedback loop
        generated_text = self._generate_text_with_validation_and_feedback(
            ideas_content, template_content, max_attempts=3
        )
        
        # Read existing history if output file exists
        history = []
        if os.path.exists(output_file_path):
            try:
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                    # Parse existing history (format: timestamp-separated entries)
                    history = self._parse_history(existing_content)
            except Exception as e:
                print(f"Warning: Failed to read existing history: {e}. Starting fresh.")
        
        # Create new entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "timestamp": timestamp,
            "text": generated_text,
            "ideas_file": ideas_file_path,
            "template_file": template_file_path
        }
        
        # Add new entry at the beginning (latest first)
        history.insert(0, new_entry)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise IOError(f"Failed to create output directory '{output_dir}': {str(e)}")
        
        # Write history to output file (latest first)
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(history):
                    f.write(f"{'=' * 80}\n")
                    f.write(f"REVISION #{len(history) - i}\n")
                    f.write(f"Timestamp: {entry['timestamp']}\n")
                    f.write(f"Ideas File: {entry['ideas_file']}\n")
                    f.write(f"Template File: {entry['template_file']}\n")
                    f.write(f"{'=' * 80}\n\n")
                    f.write(entry['text'])
                    f.write("\n\n")
        except Exception as e:
            raise IOError(f"Failed to write output file '{output_file_path}': {str(e)}")
        
        # Save generated text in LaTeX format to latex-final.txt (using AI to format with LaTeX commands)
        latex_output_path = "latex-final.txt"
        try:
            latex_content = self._convert_to_latex_with_ai(generated_text)
            with open(latex_output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            print(f"✓ LaTeX formatted text saved to: {latex_output_path}")
        except Exception as e:
            print(f"Warning: Failed to write LaTeX file '{latex_output_path}': {str(e)}")
        
        # Add to draft history
        draft_entry = {
            "ideas_file": ideas_file_path,
            "template_file": template_file_path,
            "content": generated_text,
            "timestamp": timestamp,
            "latex_file": latex_output_path
        }
        self.draft_history.append(draft_entry)
        
        return {
            "generated_text": generated_text,
            "ideas_file": ideas_file_path,
            "template_file": template_file_path,
            "output_file": output_file_path,
            "latex_file": latex_output_path,
            "timestamp": timestamp
        }
    
    def revise_from_todo_list(self, todo_list_file_path: str, 
                               writinghistory_file_path: str,
                               ideas_file_path: Optional[str] = None,
                               template_file_path: Optional[str] = None) -> Dict:
        """
        Revise the latest writing based on a todo list, and save to writing history.
        
        Args:
            todo_list_file_path: Path to text file containing actionable to-do list
            writinghistory_file_path: Path to writinghistory.txt containing all writing revisions
            ideas_file_path: Optional path to ideas file (to maintain consistency)
            template_file_path: Optional path to template file (to maintain consistency)
        
        Returns:
            Dictionary containing:
            - revised_text: The revised text content
            - todo_list: The todo list used
            - original_writing: The original writing that was revised
            - output_file: Path to updated writing history file
            - timestamp: Timestamp of revision
        """
        if not self.api_available:
            raise ValueError(
                f"API ({self.api_provider}) is not available. "
                "Please configure the API key or install the required library."
            )
        
        # Check if input files exist
        if not os.path.exists(todo_list_file_path):
            raise FileNotFoundError(f"Todo list file not found: {todo_list_file_path}")
        if not os.path.exists(writinghistory_file_path):
            raise FileNotFoundError(f"Writing history file not found: {writinghistory_file_path}")
        
        # Read todo list file (may contain history or just plain text)
        try:
            with open(todo_list_file_path, 'r', encoding='utf-8') as f:
                todo_list_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read todo list file '{todo_list_file_path}': {str(e)}")
        
        if not todo_list_content.strip():
            raise ValueError(f"Todo list file '{todo_list_file_path}' is empty")
        
        # Extract latest todo list if file contains history format
        # CRITICAL: Only use the latest to-do list, ignore any older ones
        has_history = "TODO LIST #" in todo_list_content
        todo_list_content = self._extract_latest_todo_from_file(todo_list_content)
        
        if not todo_list_content.strip():
            raise ValueError(f"No valid todo list found in '{todo_list_file_path}'")
        
        # Log which todo list is being used (for debugging/clarity)
        if has_history:
            print(f"Note: Extracted latest to-do list from history format. Older to-do lists are ignored.")
        
        # Read writing history and extract latest writing
        try:
            with open(writinghistory_file_path, 'r', encoding='utf-8') as f:
                history_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read writing history file '{writinghistory_file_path}': {str(e)}")
        
        if not history_content.strip():
            raise ValueError(f"Writing history file '{writinghistory_file_path}' is empty")
        
        # Extract latest writing and its metadata
        latest_writing_data = self._extract_latest_writing_with_metadata(history_content)
        
        if not latest_writing_data or not latest_writing_data.get("text"):
            raise ValueError(f"No valid writing found in '{writinghistory_file_path}'")
        
        original_writing = latest_writing_data["text"]
        original_ideas_file = latest_writing_data.get("ideas_file", ideas_file_path or "unknown")
        original_template_file = latest_writing_data.get("template_file", template_file_path or "unknown")
        
        # Use provided paths or fall back to original
        ideas_file = ideas_file_path or original_ideas_file
        template_file = template_file_path or original_template_file
        
        # Generate revised text using AI
        revised_text = self._revise_text_with_ai(original_writing, todo_list_content, ideas_file, template_file)
        
        # Read existing history
        history = []
        if history_content.strip():
            history = self._parse_history(history_content)
        
        # Create new revision entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "timestamp": timestamp,
            "text": revised_text,
            "ideas_file": ideas_file,
            "template_file": template_file
        }
        
        # Add new entry at the beginning (latest first)
        history.insert(0, new_entry)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(writinghistory_file_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise IOError(f"Failed to create output directory '{output_dir}': {str(e)}")
        
        # Write updated history to file (latest first)
        try:
            with open(writinghistory_file_path, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(history):
                    f.write(f"{'=' * 80}\n")
                    f.write(f"REVISION #{len(history) - i}\n")
                    f.write(f"Timestamp: {entry['timestamp']}\n")
                    f.write(f"Ideas File: {entry['ideas_file']}\n")
                    f.write(f"Template File: {entry['template_file']}\n")
                    f.write(f"{'=' * 80}\n\n")
                    f.write(entry['text'])
                    f.write("\n\n")
        except Exception as e:
            raise IOError(f"Failed to write writing history file '{writinghistory_file_path}': {str(e)}")
        
        # Save revised text in LaTeX format to latex-final.txt (using AI to format with LaTeX commands)
        latex_output_path = "latex-final.txt"
        try:
            latex_content = self._convert_to_latex_with_ai(revised_text)
            with open(latex_output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            print(f"✓ LaTeX formatted text saved to: {latex_output_path}")
        except Exception as e:
            print(f"Warning: Failed to write LaTeX file '{latex_output_path}': {str(e)}")
        
        # Add to draft history
        draft_entry = {
            "todo_list_file": todo_list_file_path,
            "original_text": original_writing,
            "revised_text": revised_text,
            "ideas_file": ideas_file,
            "template_file": template_file,
            "timestamp": timestamp,
            "latex_file": latex_output_path
        }
        self.draft_history.append(draft_entry)
        
        return {
            "revised_text": revised_text,
            "todo_list": todo_list_content,
            "original_writing": original_writing,
            "output_file": writinghistory_file_path,
            "latex_file": latex_output_path,
            "timestamp": timestamp
        }
    
    def _extract_latest_writing_with_metadata(self, history_content: str) -> Dict:
        """
        Extract the latest writing from history file along with metadata.
        
        Returns:
            Dictionary with 'text', 'ideas_file', 'template_file', 'timestamp'
        """
        # Find the first revision block (latest is at top)
        pattern = r'={80}\nREVISION #(\d+)\nTimestamp:\s*(.+?)\nIdeas File:\s*(.+?)\nTemplate File:\s*(.+?)\n={80}\n\n(.*?)(?=\n={80}\n|$)'
        match = re.search(pattern, history_content, re.DOTALL)
        
        if match:
            revision_num = match.group(1)
            timestamp = match.group(2).strip()
            ideas_file = match.group(3).strip()
            template_file = match.group(4).strip()
            text = match.group(5).strip()
            
            return {
                "revision_num": revision_num,
                "timestamp": timestamp,
                "ideas_file": ideas_file,
                "template_file": template_file,
                "text": text
            }
        
        return {}
    
    def _extract_latest_todo_from_file(self, content: str) -> str:
        """
        Extract the latest todo list from file content.
        Supports both plain text format and history format.
        
        CRITICAL: Only extracts the LATEST to-do list from history.
        All older to-do lists are ignored.
        
        Returns:
            Latest todo list content (plain text)
        """
        # Check if it's a history format (has TODO LIST # markers)
        if "TODO LIST #" in content:
            # Extract ONLY the latest (first) todo list from history
            # Pattern matches the first occurrence (latest is at top)
            pattern = r'={80}\nTODO LIST #(\d+)\nTimestamp:\s*(.+?)\nHeuristics File:\s*.+?\nWriting History File:\s*.+?\n={80}\n\n(.*?)(?=\n={80}\n|$)'
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                todo_num = match.group(1)
                timestamp = match.group(2).strip()
                todo_content = match.group(3).strip()
                
                # Verify this is the latest (should be TODO LIST #1 or highest number)
                # But since latest is at top, first match is always the latest
                print(f"Using latest to-do list (TODO LIST #{todo_num}, timestamp: {timestamp})")
                return todo_content
            
            # If pattern doesn't match, fall through to plain text
        
        # Otherwise, treat as plain text
        return content.strip()
    
    def _convert_to_latex_with_ai(self, text: str) -> str:
        """
        Convert plain text to LaTeX formatted text using AI API.
        Outputs only the formatted text content (with enumerate, textbf, etc.), not a complete document.
        
        Args:
            text: Plain text content
            
        Returns:
            LaTeX formatted text content (not a complete document)
        """
        if not self.api_available:
            # Fallback to basic formatting if API not available
            return self._convert_to_latex_basic(text)
        
        if self.api_provider == "gemini":
            return self._convert_to_latex_with_gemini(text)
        elif self.api_provider == "openai":
            return self._convert_to_latex_with_openai(text)
        else:
            return self._convert_to_latex_basic(text)
    
    def _convert_to_latex_with_gemini(self, text: str) -> str:
        """Convert to LaTeX formatted text using Gemini API."""
        prompt = f"""Convert the following academic text to LaTeX format. Output ONLY the formatted text content (NOT a complete LaTeX document).

CRITICAL REQUIREMENTS:
1. Output ONLY the body content with LaTeX formatting commands
2. Do NOT include any document structure (no \\documentclass, \\usepackage, \\begin{{document}}, etc.)
3. Use LaTeX commands appropriately:
   - \\textbf{{text}} for bold/important terms and concepts
   - \\textit{{text}} for italic/emphasis
   - \\begin{{enumerate}} ... \\end{{enumerate}} for numbered lists
   - \\begin{{itemize}} ... \\end{{itemize}} for bullet lists
   - \\section{{title}} for main section headings
   - \\subsection{{title}} for subsection headings

4. Format the text naturally - add \\textbf where important terms appear, use enumerate/itemize for lists
5. Keep the same structure and flow as the original text
6. Output ONLY the formatted text content, nothing else

Text to convert:
{text}

Convert to LaTeX formatted text (content only, no document structure):"""

        try:
            response = self.api_model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                latex_content = response.text.strip()
                return latex_content
            else:
                raise ValueError("Empty response from Gemini API")
        except Exception as e:
            print(f"Warning: Failed to convert to LaTeX with Gemini: {str(e)}. Using basic conversion.")
            return self._convert_to_latex_basic(text)
    
    def _convert_to_latex_with_openai(self, text: str) -> str:
        """Convert to LaTeX formatted text using OpenAI API."""
        prompt = f"""Convert the following academic text to LaTeX format. Output ONLY the formatted text content (NOT a complete LaTeX document).

CRITICAL REQUIREMENTS:
1. Output ONLY the body content with LaTeX formatting commands
2. Do NOT include any document structure (no \\documentclass, \\usepackage, \\begin{{document}}, etc.)
3. Use LaTeX commands appropriately:
   - \\textbf{{text}} for bold/important terms and concepts
   - \\textit{{text}} for italic/emphasis
   - \\begin{{enumerate}} ... \\end{{enumerate}} for numbered lists
   - \\begin{{itemize}} ... \\end{{itemize}} for bullet lists
   - \\section{{title}} for main section headings
   - \\subsection{{title}} for subsection headings

4. Format the text naturally - add \\textbf where important terms appear, use enumerate/itemize for lists
5. Keep the same structure and flow as the original text
6. Output ONLY the formatted text content, nothing else

Text to convert:
{text}

Convert to LaTeX formatted text (content only, no document structure):"""

        try:
            response = self.api_model.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in LaTeX formatting. Convert plain text to LaTeX formatted content (enumerate, textbf, etc.) without document structure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            if response and response.choices:
                latex_content = response.choices[0].message.content.strip()
                return latex_content
            else:
                raise ValueError("Empty response from OpenAI API")
        except Exception as e:
            print(f"Warning: Failed to convert to LaTeX with OpenAI: {str(e)}. Using basic conversion.")
            return self._convert_to_latex_basic(text)
    
    def _convert_to_latex_basic(self, text: str) -> str:
        """
        Basic LaTeX formatting fallback (if AI is not available).
        Adds basic formatting commands like textbf for important terms.
        
        Args:
            text: Plain text content
            
        Returns:
            Basic LaTeX formatted text
        """
        # Simple conversion: just escape special characters and add minimal formatting
        lines = text.split('\n')
        result = []
        
        for line in lines:
            line = line.strip()
            if not line:
                result.append("")
                continue
            
            # Convert markdown headings
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('# ').strip()
                heading_text = self._escape_latex(heading_text)
                if level == 1:
                    result.append(f"\\section{{{heading_text}}}")
                elif level == 2:
                    result.append(f"\\subsection{{{heading_text}}}")
                else:
                    result.append(f"\\subsubsection{{{heading_text}}}")
            else:
                # Regular text - escape LaTeX special characters
                escaped_line = self._escape_latex(line)
                result.append(escaped_line)
        
        return "\n".join(result)
    
    def _escape_latex(self, text: str) -> str:
        """
        Escape LaTeX special characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # LaTeX special characters that need escaping
        # Order matters: handle backslash first to avoid double-escaping
        result = text
        
        # Escape backslash first (before other replacements)
        result = result.replace('\\', r'\textbackslash{}')
        
        # Then escape other special characters
        result = result.replace('{', r'\{')
        result = result.replace('}', r'\}')
        result = result.replace('$', r'\$')
        result = result.replace('&', r'\&')
        result = result.replace('%', r'\%')
        result = result.replace('#', r'\#')
        result = result.replace('^', r'\textasciicircum{}')
        result = result.replace('_', r'\_')
        result = result.replace('~', r'\textasciitilde{}')
        
        return result
    
    def _revise_text_with_ai(self, original_text: str, todo_list: str, 
                             ideas_file: str, template_file: str) -> str:
        """
        Revise text using AI API based on todo list.
        
        Args:
            original_text: Original text to revise
            todo_list: Todo list with feedback
            ideas_file: Path to ideas file (for context)
            template_file: Path to template file (for context)
            
        Returns:
            Revised text content
        """
        # Optionally read ideas and template for context
        ideas_context = ""
        template_context = ""
        
        if os.path.exists(ideas_file):
            try:
                with open(ideas_file, 'r', encoding='utf-8') as f:
                    ideas_context = f.read()
            except:
                pass
        
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_context = f.read()
            except:
                pass
        
        if self.api_provider == "gemini":
            return self._revise_with_gemini(original_text, todo_list, ideas_context, template_context)
        elif self.api_provider == "openai":
            return self._revise_with_openai(original_text, todo_list, ideas_context, template_context)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _revise_with_gemini(self, original_text: str, todo_list: str, 
                           ideas_context: str, template_context: str) -> str:
        """Revise text using Google Gen AI SDK (Gemini API)."""
        prompt = f"""You are a student revising your research paper draft based on professor feedback. Revise the writing to address all items in the to-do list.

ORIGINAL DRAFT (to be revised):
{original_text}

PROFESSOR'S TO-DO LIST (address ALL items):
{todo_list}
"""

        if ideas_context:
            prompt += f"""

ORIGINAL IDEAS (maintain focus on these):
{ideas_context}
"""

        if template_context:
            prompt += f"""

TEMPLATE STRUCTURE (maintain this flow):
{template_context}
"""

        prompt += """

INSTRUCTIONS:
1. Carefully review each item in the to-do list
2. Revise the original draft to address ALL to-do items
3. Maintain the core ideas and focus from the original ideas
4. Keep the overall structure and flow
5. Make improvements as specified in the to-do list
6. Ensure the revised text is coherent and well-written
7. Do NOT simply list the changes - integrate them naturally into the text
8. If a to-do item asks to add something, add it appropriately
9. If a to-do item asks to clarify something, make it clearer
10. If a to-do item asks to remove something, remove it

Generate the complete revised text now:"""

        try:
            response = self.api_model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                revised_text = response.text.strip()
                return revised_text
            else:
                raise ValueError("Empty response from Gemini API")
        except Exception as e:
            raise RuntimeError(f"Error calling Gemini API: {str(e)}")
    
    def _revise_with_openai(self, original_text: str, todo_list: str,
                           ideas_context: str, template_context: str) -> str:
        """Revise text using OpenAI API."""
        prompt = f"""You are a student revising your research paper draft based on professor feedback. Revise the writing to address all items in the to-do list.

ORIGINAL DRAFT (to be revised):
{original_text}

PROFESSOR'S TO-DO LIST (address ALL items):
{todo_list}
"""

        if ideas_context:
            prompt += f"""

ORIGINAL IDEAS (maintain focus on these):
{ideas_context}
"""

        if template_context:
            prompt += f"""

TEMPLATE STRUCTURE (maintain this flow):
{template_context}
"""

        prompt += """

INSTRUCTIONS:
1. Carefully review each item in the to-do list
2. Revise the original draft to address ALL to-do items
3. Maintain the core ideas and focus from the original ideas
4. Keep the overall structure and flow
5. Make improvements as specified in the to-do list
6. Ensure the revised text is coherent and well-written
7. Do NOT simply list the changes - integrate them naturally into the text
8. If a to-do item asks to add something, add it appropriately
9. If a to-do item asks to clarify something, make it clearer
10. If a to-do item asks to remove something, remove it

Generate the complete revised text now:"""

        try:
            response = self.api_model.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a student revising your academic writing based on professor feedback. Integrate all feedback naturally into the text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            if response and response.choices:
                revised_text = response.choices[0].message.content.strip()
                return revised_text
            else:
                raise ValueError("Empty response from OpenAI API")
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")
    
    def _parse_history(self, content: str) -> List[Dict]:
        """
        Parse existing history from output file.
        
        Format:
        ================================================================================
        REVISION #N
        Timestamp: ...
        Ideas File: ...
        Template File: ...
        ================================================================================
        
        [text content]
        """
        history = []
        # Split by separator blocks (80 equal signs with newlines)
        # Pattern: ={80}\nREVISION #...\n...\n={80}\n\n[text]
        pattern = r'={80}\n(REVISION #\d+.*?)={80}\n\n(.*?)(?=\n={80}\n|$)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            metadata_block = match.group(1)
            text_content = match.group(2).strip()
            
            if not text_content:
                continue
            
            # Extract metadata from the block
            timestamp_match = re.search(r'Timestamp:\s*(.+)', metadata_block)
            ideas_match = re.search(r'Ideas File:\s*(.+)', metadata_block)
            template_match = re.search(r'Template File:\s*(.+)', metadata_block)
            
            if timestamp_match and ideas_match and template_match:
                history.append({
                    "timestamp": timestamp_match.group(1).strip(),
                    "ideas_file": ideas_match.group(1).strip(),
                    "template_file": template_match.group(1).strip(),
                    "text": text_content
                })
        
        return history
    
    def _generate_text_with_validation_and_feedback(self, ideas: str, template: str, max_attempts: int = 3) -> str:
        """
        Generate text using AI API with validation and feedback loop.
        Ensures generated content is relevant to the key ideas.
        
        Args:
            ideas: Main ideas content
            template: Template structure
            max_attempts: Maximum number of regeneration attempts
            
        Returns:
            Generated text content that is relevant to ideas
        """
        # Extract key concepts from ideas
        key_concepts = self._extract_key_concepts(ideas)
        
        for attempt in range(max_attempts):
            # Generate text
            if self.api_provider == "gemini":
                generated_text = self._generate_with_gemini(ideas, template, feedback=None if attempt == 0 else f"Previous attempt contained content not relevant to the key ideas. Focus ONLY on: {', '.join(key_concepts)}")
            elif self.api_provider == "openai":
                generated_text = self._generate_with_openai(ideas, template, feedback=None if attempt == 0 else f"Previous attempt contained content not relevant to the key ideas. Focus ONLY on: {', '.join(key_concepts)}")
            else:
                raise ValueError(f"Unsupported API provider: {self.api_provider}")
            
            # Validate relevance
            is_relevant, issues = self._validate_relevance(generated_text, key_concepts, ideas)
            
            if is_relevant:
                return generated_text
            else:
                print(f"Warning: Generated text contains irrelevant content (attempt {attempt + 1}/{max_attempts})")
                print(f"  Issues found: {', '.join(issues[:3])}")
                
                if attempt < max_attempts - 1:
                    # Prepare feedback for regeneration
                    feedback = f"""The generated text contains content that is NOT relevant to the key ideas. 

SPECIFIC ISSUES TO FIX:
{chr(10).join('- ' + issue for issue in issues[:5])}

CRITICAL: Focus ONLY on these key ideas: {', '.join(key_concepts)}

Do NOT include any content about:
- Topics not mentioned in the ideas file
- Concepts, tools, or methods from the template file that don't relate to the key ideas
- Citations or references to papers unrelated to the core topic

Regenerate the text focusing STRICTLY on the key ideas provided."""
                    
                    # Regenerate with feedback
                    if self.api_provider == "gemini":
                        generated_text = self._generate_with_gemini(ideas, template, feedback=feedback)
                    else:
                        generated_text = self._generate_with_openai(ideas, template, feedback=feedback)
                    
                    # Validate again
                    is_relevant, new_issues = self._validate_relevance(generated_text, key_concepts, ideas)
                    if is_relevant:
                        return generated_text
        
        # If all attempts failed, return the last attempt with a warning
        print(f"Warning: Could not generate fully relevant text after {max_attempts} attempts. Returning best attempt.")
        return generated_text
    
    def _extract_key_concepts(self, ideas: str) -> List[str]:
        """
        Extract key concepts and terms from ideas text.
        
        Args:
            ideas: Ideas text
            
        Returns:
            List of key concepts
        """
        # Extract key terms (simple heuristic: important capitalized words, tool names, etc.)
        concepts = []
        
        # Look for tool/project names (capitalized words that appear multiple times)
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', ideas)
        word_counts = Counter(words)
        concepts.extend([word for word, count in word_counts.most_common(5) if count >= 1])
        
        # Look for quoted or emphasized terms
        quoted = re.findall(r'["\']([^"\']+)["\']', ideas)
        concepts.extend(quoted)
        
        # Look for ALL CAPS terms
        all_caps = re.findall(r'\b[A-Z]{2,}\b', ideas)
        concepts.extend(all_caps)
        
        # Remove duplicates and common words
        common_words = {'The', 'This', 'We', 'Our', 'They', 'That', 'These', 'Paper', 'Research', 'Study'}
        concepts = [c for c in set(concepts) if c not in common_words and len(c) > 2]
        
        return concepts[:10]  # Return top 10 concepts
    
    def _validate_relevance(self, generated_text: str, key_concepts: List[str], ideas: str) -> Tuple[bool, List[str]]:
        """
        Validate if generated text is relevant to key ideas.
        
        Args:
            generated_text: Generated text to validate
            key_concepts: Key concepts that must be present
            ideas: Original ideas text for reference
            
        Returns:
            Tuple of (is_relevant, list_of_issues)
        """
        issues = []
        generated_lower = generated_text.lower()
        ideas_lower = ideas.lower()
        
        # Check if key concepts are mentioned
        missing_concepts = []
        for concept in key_concepts[:5]:  # Check top 5 concepts
            if concept.lower() not in generated_lower:
                missing_concepts.append(concept)
        
        if missing_concepts:
            issues.append(f"Missing key concepts: {', '.join(missing_concepts)}")
        
        # Check for content that seems unrelated (heuristic: check if ideas keywords appear)
        ideas_keywords = set(re.findall(r'\b[a-z]{4,}\b', ideas_lower))
        generated_keywords = set(re.findall(r'\b[a-z]{4,}\b', generated_lower))
        
        # Check overlap - if very low, might be irrelevant
        overlap = len(ideas_keywords & generated_keywords) / max(len(ideas_keywords), 1)
        if overlap < 0.3:  # Less than 30% keyword overlap
            issues.append(f"Low keyword overlap with ideas ({overlap:.1%})")
        
        # Check for common template noise patterns (citations, unrelated tools)
        # Extract potential noise from template (not implemented here, but can be enhanced)
        
        # If multiple key concepts are missing or overlap is very low, consider irrelevant
        is_relevant = len(missing_concepts) < 3 and overlap >= 0.2
        
        return is_relevant, issues
    
    def _generate_with_gemini(self, ideas: str, template: str, feedback: Optional[str] = None) -> str:
        """
        Generate text using Google Gen AI SDK (Gemini API).
        
        Args:
            ideas: Main ideas content
            template: Template structure (used only as a guide for structure, ignore content noise)
            feedback: Optional feedback for regeneration
        """
        if feedback:
            prompt = f"""You are an academic writer. REGENERATE the text based on the feedback below.

FEEDBACK ON PREVIOUS ATTEMPT:
{feedback}

MAIN IDEAS TO INCLUDE (THIS IS YOUR PRIMARY FOCUS):
{ideas}

TEMPLATE STRUCTURE (use ONLY for sentence structure/flow patterns, IGNORE any specific content or concepts):
{template}

CRITICAL INSTRUCTIONS:
1. Focus STRICTLY on the key ideas provided above - do NOT include content from the template that doesn't relate to these ideas
2. The template is ONLY for understanding sentence roles and flow - ignore any specific concepts, tools, or methods mentioned in the template
3. Generate text that incorporates ALL the main ideas from the ideas section
4. Write in academic style with proper flow and transitions
5. Do NOT include citations, references, or concepts from the template file unless they directly relate to the key ideas
6. Ensure the content is coherent, well-structured, and follows academic writing conventions

Generate the complete section text now, focusing ONLY on the key ideas:"""
        else:
            prompt = f"""You are an academic writer. Generate a well-written research paper section based on the provided ideas.

PRIMARY SOURCE - MAIN IDEAS TO INCLUDE (THIS IS YOUR MAIN FOCUS):
{ideas}

SECONDARY REFERENCE - TEMPLATE STRUCTURE (use ONLY for understanding sentence roles and flow patterns):
{template}

CRITICAL INSTRUCTIONS:
1. PRIORITIZE the ideas file - focus STRICTLY on incorporating ALL the key ideas provided above
2. The template file is ONLY for understanding sentence structure and flow patterns - IGNORE any specific content, concepts, tools, methods, or citations mentioned in it
3. If the template contains content unrelated to your key ideas (e.g., different tools, papers, or concepts), completely ignore that content
4. Extract only the structural pattern from the template (e.g., [establishes background] → [introduces problem] → [presents solution])
5. Write in academic style with proper flow and transitions
6. Do NOT include template markers in your output - write actual content instead
7. Ensure every sentence relates to the key ideas - do NOT add content about unrelated topics from the template

Generate the complete section text now, focusing STRICTLY on the key ideas:"""

        try:
            response = self.api_model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                generated_text = response.text.strip()
                return generated_text
            else:
                raise ValueError("Empty response from Gemini API")
        except Exception as e:
            raise RuntimeError(f"Error calling Gemini API: {str(e)}")
    
    def _generate_with_openai(self, ideas: str, template: str, feedback: Optional[str] = None) -> str:
        """
        Generate text using OpenAI API.
        
        Args:
            ideas: Main ideas content
            template: Template structure (used only as a guide for structure, ignore content noise)
            feedback: Optional feedback for regeneration
        """
        if feedback:
            prompt = f"""You are an academic writer. REGENERATE the text based on the feedback below.

FEEDBACK ON PREVIOUS ATTEMPT:
{feedback}

MAIN IDEAS TO INCLUDE (THIS IS YOUR PRIMARY FOCUS):
{ideas}

TEMPLATE STRUCTURE (use ONLY for sentence structure/flow patterns, IGNORE any specific content or concepts):
{template}

CRITICAL INSTRUCTIONS:
1. Focus STRICTLY on the key ideas provided above - do NOT include content from the template that doesn't relate to these ideas
2. The template is ONLY for understanding sentence roles and flow - ignore any specific concepts, tools, or methods mentioned in the template
3. Generate text that incorporates ALL the main ideas from the ideas section
4. Write in academic style with proper flow and transitions
5. Do NOT include citations, references, or concepts from the template file unless they directly relate to the key ideas
6. Ensure the content is coherent, well-structured, and follows academic writing conventions

Generate the complete section text now, focusing ONLY on the key ideas:"""
        else:
            prompt = f"""You are an academic writer. Generate a well-written research paper section based on the provided ideas.

PRIMARY SOURCE - MAIN IDEAS TO INCLUDE (THIS IS YOUR MAIN FOCUS):
{ideas}

SECONDARY REFERENCE - TEMPLATE STRUCTURE (use ONLY for understanding sentence roles and flow patterns):
{template}

CRITICAL INSTRUCTIONS:
1. PRIORITIZE the ideas file - focus STRICTLY on incorporating ALL the key ideas provided above
2. The template file is ONLY for understanding sentence structure and flow patterns - IGNORE any specific content, concepts, tools, methods, or citations mentioned in it
3. If the template contains content unrelated to your key ideas (e.g., different tools, papers, or concepts), completely ignore that content
4. Extract only the structural pattern from the template (e.g., [establishes background] → [introduces problem] → [presents solution])
5. Write in academic style with proper flow and transitions
6. Do NOT include template markers in your output - write actual content instead
7. Ensure every sentence relates to the key ideas - do NOT add content about unrelated topics from the template

Generate the complete section text now, focusing STRICTLY on the key ideas:"""

        try:
            response = self.api_model.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert academic writer. Generate well-structured research paper content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            if response and response.choices:
                generated_text = response.choices[0].message.content.strip()
                return generated_text
            else:
                raise ValueError("Empty response from OpenAI API")
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")

