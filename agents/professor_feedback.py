"""
 python generate_feedback.py "heuristics.txt" "writinghistory.txt" "todo_list.txt"

Professor Feedback Agent
Provides academic feedback similar to a professor reviewing a research paper.
Uses AI APIs to generate actionable to-do lists based on heuristics.
"""

from typing import Dict, List, Optional
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


class ProfessorFeedbackAgent:
    """Agent that acts as a professor providing academic feedback."""
    
    def __init__(self, name: str = "Professor Feedback", 
                 expertise: str = "General Academic",
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Professor Feedback Agent.
        
        Args:
            name: Name of the agent
            expertise: Area of expertise
            api_provider: AI API provider to use ("gemini" or "openai")
            gemini_api_key: Optional Gemini API key. If not provided, will try GEMINI_API_KEY env variable.
            openai_api_key: Optional OpenAI API key. If not provided, will try OPENAI_API_KEY env variable.
        """
        self.name = name
        self.expertise = expertise
        self.feedback_history = []
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
            print(f"✓ Google Gen AI SDK configured for feedback generation")
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
            print(f"✓ OpenAI API configured for feedback generation")
        except Exception as e:
            print(f"Warning: Failed to configure OpenAI API: {str(e)}")
            self.api_available = False
    
    def review_paper(self, paper: Dict[str, str], topic: str, 
                     style_analysis: Optional[Dict] = None) -> Dict:
        """
        Provide comprehensive professor feedback on the paper.
        
        Args:
            paper: Dictionary mapping section names to content
            topic: The research topic
            style_analysis: Optional style analysis from StyleAnalyzerAgent
            
        Returns:
            Dictionary containing professor feedback
        """
        feedback = {
            "overall_assessment": "",
            "strengths": [],
            "weaknesses": [],
            "section_feedback": {},
            "suggestions_for_improvement": [],
            "grade_estimate": "",
            "specific_comments": []
        }
        
        # Overall assessment
        feedback["overall_assessment"] = self._provide_overall_assessment(paper, topic)
        
        # Review each section
        for section_name, content in paper.items():
            section_fb = self.review_section(section_name, content, topic)
            feedback["section_feedback"][section_name] = section_fb
        
        # Aggregate feedback
        feedback["strengths"] = self._identify_overall_strengths(paper, topic)
        feedback["weaknesses"] = self._identify_overall_weaknesses(paper, topic)
        feedback["suggestions_for_improvement"] = self._generate_improvement_suggestions(paper, style_analysis)
        feedback["grade_estimate"] = self._estimate_grade(feedback, style_analysis)
        feedback["specific_comments"] = self._generate_specific_comments(paper, topic)
        
        self.feedback_history.append(feedback)
        
        return feedback
    
    def review_section(self, section_name: str, content: str, topic: str) -> Dict:
        """
        Provide feedback on a specific section.
        
        Args:
            section_name: Name of the section
            content: Section content
            topic: The research topic
            
        Returns:
            Dictionary containing section-specific feedback
        """
        section_feedback = {
            "assessment": "",
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        # Provide assessment
        section_feedback["assessment"] = self._assess_section(section_name, content, topic)
        
        # Section-specific checks
        if section_name.lower() == "introduction":
            section_feedback.update(self._review_introduction(content, topic))
        elif section_name.lower() == "methodology":
            section_feedback.update(self._review_methodology(content, topic))
        elif section_name.lower() == "results":
            section_feedback.update(self._review_results(content, topic))
        elif section_name.lower() == "discussion":
            section_feedback.update(self._review_discussion(content, topic))
        elif section_name.lower() == "conclusion":
            section_feedback.update(self._review_conclusion(content, topic))
        else:
            section_feedback.update(self._review_generic_section(section_name, content, topic))
        
        return section_feedback
    
    def _provide_overall_assessment(self, paper: Dict[str, str], topic: str) -> str:
        """Provide overall assessment of the paper."""
        total_words = sum(len(content.split()) for content in paper.values())
        section_count = len(paper)
        
        assessment = f"""This paper on '{topic}' presents a {section_count}-section investigation. 
        The paper contains approximately {total_words} words total. """
        
        if total_words < 1500:
            assessment += "The paper appears somewhat brief and may benefit from more comprehensive coverage of the topic. "
        elif total_words > 8000:
            assessment += "The paper is quite comprehensive in length. "
        else:
            assessment += "The paper has an appropriate length for the scope of research. "
        
        # Check for key sections
        required_sections = ["introduction", "methodology", "results", "discussion", "conclusion"]
        present_sections = [s.lower() for s in paper.keys()]
        missing_sections = [s for s in required_sections if s not in present_sections]
        
        if missing_sections:
            assessment += f"Note that some standard sections are missing: {', '.join(missing_sections)}. "
        
        assessment += "Overall, this is a solid effort that demonstrates understanding of the research process."
        
        return assessment
    
    def _assess_section(self, section_name: str, content: str, topic: str) -> str:
        """Assess a specific section."""
        word_count = len(content.split())
        
        assessment = f"The {section_name} section ({word_count} words) "
        
        if word_count < 100:
            assessment += "is quite brief and may need expansion. "
        elif word_count > 2000:
            assessment += "is comprehensive but may be too lengthy for a single section. "
        else:
            assessment += "has an appropriate length. "
        
        if "#" in content:
            assessment += "The section is well-structured with clear subsections. "
        
        assessment += "The content relates appropriately to the topic."
        
        return assessment
    
    def _review_introduction(self, content: str, topic: str) -> Dict:
        """Review introduction section specifically."""
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        # Check for research question/hypothesis
        has_research_q = any(phrase in content.lower() for phrase in 
                           ['research question', 'objective', 'aim', 'hypothesis', 'purpose'])
        
        if has_research_q:
            feedback["strengths"].append("The introduction clearly states research objectives")
        else:
            feedback["weaknesses"].append("The introduction should more explicitly state the research question or objectives")
            feedback["recommendations"].append("Add a clear statement of research objectives or hypotheses")
        
        # Check for context/background
        has_background = any(phrase in content.lower() for phrase in 
                           ['background', 'context', 'previous research', 'literature'])
        
        if has_background:
            feedback["strengths"].append("Good contextual background is provided")
        else:
            feedback["weaknesses"].append("More background or context would strengthen the introduction")
            feedback["recommendations"].append("Include more background information about the topic")
        
        # Check for paper organization
        if 'organized' in content.lower() or 'structure' in content.lower():
            feedback["strengths"].append("The introduction mentions paper organization, which helps readers")
        
        return feedback
    
    def _review_methodology(self, content: str, topic: str) -> Dict:
        """Review methodology section specifically."""
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        # Check for research design
        has_design = any(phrase in content.lower() for phrase in 
                        ['research design', 'method', 'approach', 'design'])
        
        if has_design:
            feedback["strengths"].append("The methodology describes the research design")
        else:
            feedback["weaknesses"].append("The methodology should more clearly describe the research design")
            feedback["recommendations"].append("Elaborate on the specific research design and rationale")
        
        # Check for data collection
        if 'data collection' in content.lower() or 'data' in content.lower():
            feedback["strengths"].append("Data collection procedures are mentioned")
        else:
            feedback["weaknesses"].append("More detail on data collection would strengthen the methodology")
            feedback["recommendations"].append("Provide more specific details about data collection procedures")
        
        # Check for analysis methods
        if 'analysis' in content.lower() or 'method' in content.lower():
            feedback["strengths"].append("Analysis methods are discussed")
        else:
            feedback["recommendations"].append("Describe the analytical methods in more detail")
        
        return feedback
    
    def _review_results(self, content: str, topic: str) -> Dict:
        """Review results section specifically."""
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        # Check for findings
        has_findings = any(phrase in content.lower() for phrase in 
                         ['finding', 'result', 'observed', 'showed', 'demonstrated'])
        
        if has_findings:
            feedback["strengths"].append("Findings are clearly presented")
        else:
            feedback["weaknesses"].append("The results section should more explicitly state the findings")
            feedback["recommendations"].append("Make findings more explicit and clear")
        
        # Check for statistics
        if 'statistical' in content.lower() or 'significant' in content.lower():
            feedback["strengths"].append("Statistical analysis is mentioned")
        else:
            feedback["recommendations"].append("Consider including statistical analysis of the results")
        
        return feedback
    
    def _review_discussion(self, content: str, topic: str) -> Dict:
        """Review discussion section specifically."""
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        # Check for interpretation
        has_interpretation = any(phrase in content.lower() for phrase in 
                               ['interpret', 'suggest', 'indicate', 'imply', 'mean'])
        
        if has_interpretation:
            feedback["strengths"].append("The discussion interprets the findings")
        else:
            feedback["weaknesses"].append("The discussion should provide more interpretation of results")
            feedback["recommendations"].append("Add more interpretation and explanation of what the findings mean")
        
        # Check for comparison with literature
        if any(phrase in content.lower() for phrase in 
               ['previous', 'literature', 'research', 'compare', 'consist']):
            feedback["strengths"].append("The discussion relates findings to previous research")
        else:
            feedback["recommendations"].append("Compare findings with previous literature more explicitly")
        
        # Check for implications
        if 'implication' in content.lower() or 'significance' in content.lower():
            feedback["strengths"].append("Implications are discussed")
        else:
            feedback["recommendations"].append("Discuss the implications of your findings")
        
        return feedback
    
    def _review_conclusion(self, content: str, topic: str) -> Dict:
        """Review conclusion section specifically."""
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        # Check for summary
        has_summary = any(phrase in content.lower() for phrase in 
                        ['summary', 'conclude', 'overall', 'main finding'])
        
        if has_summary:
            feedback["strengths"].append("The conclusion summarizes the work")
        else:
            feedback["weaknesses"].append("The conclusion should better summarize the main contributions")
            feedback["recommendations"].append("Provide a clearer summary of key findings and contributions")
        
        # Check for limitations
        if 'limitation' in content.lower():
            feedback["strengths"].append("The conclusion acknowledges limitations, which shows academic rigor")
        else:
            feedback["recommendations"].append("Consider discussing limitations of the study")
        
        # Check for future work
        if any(phrase in content.lower() for phrase in 
               ['future', 'further research', 'recommend', 'next step']):
            feedback["strengths"].append("Future directions are discussed")
        else:
            feedback["recommendations"].append("Suggest directions for future research")
        
        return feedback
    
    def _review_generic_section(self, section_name: str, content: str, topic: str) -> Dict:
        """Review a generic section."""
        feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_feedback": [],
            "recommendations": []
        }
        
        word_count = len(content.split())
        
        if word_count >= 150:
            feedback["strengths"].append(f"The {section_name} section has adequate content")
        else:
            feedback["weaknesses"].append(f"The {section_name} section may need more development")
            feedback["recommendations"].append(f"Expand the {section_name} section with more detail")
        
        return feedback
    
    def _identify_overall_strengths(self, paper: Dict[str, str], topic: str) -> List[str]:
        """Identify overall strengths of the paper."""
        strengths = []
        
        # Structure
        if len(paper) >= 4:
            strengths.append("The paper has a good structure with multiple sections")
        
        # Coverage
        total_words = sum(len(content.split()) for content in paper.values())
        if total_words >= 2000:
            strengths.append("The paper provides comprehensive coverage of the topic")
        
        # Academic tone
        all_content = " ".join(paper.values())
        if not any(word in all_content.lower() for word in ['gonna', 'wanna', 'lol', 'omg']):
            strengths.append("The paper maintains an appropriate academic tone throughout")
        
        return strengths
    
    def _identify_overall_weaknesses(self, paper: Dict[str, str], topic: str) -> List[str]:
        """Identify overall weaknesses of the paper."""
        weaknesses = []
        
        # Missing sections
        standard_sections = ["introduction", "methodology", "results", "discussion", "conclusion"]
        present_sections = [s.lower() for s in paper.keys()]
        missing = [s for s in standard_sections if s not in present_sections]
        
        if missing:
            weaknesses.append(f"Missing standard sections: {', '.join(missing)}")
        
        # Length
        total_words = sum(len(content.split()) for content in paper.values())
        if total_words < 1500:
            weaknesses.append("The paper is somewhat brief and could benefit from more depth")
        
        # Citations (would check if implemented)
        # weaknesses.append("The paper would benefit from proper citations and references")
        
        return weaknesses
    
    def _generate_improvement_suggestions(self, paper: Dict[str, str], 
                                        style_analysis: Optional[Dict]) -> List[str]:
        """Generate suggestions for improvement."""
        suggestions = []
        
        if style_analysis:
            score = style_analysis.get("overall_score", 1.0)
            if score < 0.7:
                suggestions.append("Focus on improving writing style and clarity")
            
            issues = style_analysis.get("style_issues", [])
            if len(issues) > 5:
                suggestions.append("Address the style issues identified in the analysis")
        
        suggestions.append("Ensure all sections flow logically from one to the next")
        suggestions.append("Consider adding more specific examples or case studies")
        suggestions.append("Review and strengthen the connection between methodology and results")
        
        return suggestions
    
    def _estimate_grade(self, feedback: Dict, style_analysis: Optional[Dict]) -> str:
        """Estimate a grade for the paper."""
        score = 0.5  # Base score
        
        # Adjust based on strengths/weaknesses
        score += len(feedback.get("strengths", [])) * 0.05
        score -= len(feedback.get("weaknesses", [])) * 0.05
        
        # Adjust based on style analysis
        if style_analysis:
            style_score = style_analysis.get("overall_score", 0.7)
            score = (score + style_score) / 2
        
        # Cap between 0.5 and 1.0
        score = max(0.5, min(1.0, score))
        
        # Convert to letter grade
        if score >= 0.93:
            return "A"
        elif score >= 0.90:
            return "A-"
        elif score >= 0.87:
            return "B+"
        elif score >= 0.83:
            return "B"
        elif score >= 0.80:
            return "B-"
        elif score >= 0.77:
            return "C+"
        elif score >= 0.70:
            return "C"
        else:
            return "C- or below (needs significant improvement)"
    
    def _generate_specific_comments(self, paper: Dict[str, str], topic: str) -> List[str]:
        """Generate specific comments on the paper."""
        comments = []
        
        comments.append("This paper demonstrates a solid understanding of research paper structure.")
        comments.append("The writing is clear and generally well-organized.")
        comments.append("Consider adding more specific details and examples to strengthen arguments.")
        comments.append("The connection between sections could be enhanced with better transitions.")
        
        return comments
    
    def generate_feedback_from_files(self, heuristics_file_path: str, 
                                     writinghistory_file_path: str, 
                                     output_file_path: str) -> Dict:
        """
        Generate actionable to-do list feedback based on heuristics and latest writing.
        
        Args:
            heuristics_file_path: Path to text file containing evaluation heuristics
            writinghistory_file_path: Path to writinghistory.txt containing all writing revisions
            output_file_path: Path to output file where the to-do list will be saved
        
        Returns:
            Dictionary containing:
            - latest_writing: The extracted latest writing
            - heuristics: The heuristics used
            - todo_list: Generated to-do list
            - output_file: Path to output file
        """
        if not self.api_available:
            raise ValueError(
                f"API ({self.api_provider}) is not available. "
                "Please configure the API key or install the required library."
            )
        
        # Check if input files exist
        if not os.path.exists(heuristics_file_path):
            raise FileNotFoundError(f"Heuristics file not found: {heuristics_file_path}")
        if not os.path.exists(writinghistory_file_path):
            raise FileNotFoundError(f"Writing history file not found: {writinghistory_file_path}")
        
        # Read heuristics file
        try:
            with open(heuristics_file_path, 'r', encoding='utf-8') as f:
                heuristics_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read heuristics file '{heuristics_file_path}': {str(e)}")
        
        if not heuristics_content.strip():
            raise ValueError(f"Heuristics file '{heuristics_file_path}' is empty")
        
        # Read writing history and extract latest writing
        try:
            with open(writinghistory_file_path, 'r', encoding='utf-8') as f:
                history_content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read writing history file '{writinghistory_file_path}': {str(e)}")
        
        if not history_content.strip():
            raise ValueError(f"Writing history file '{writinghistory_file_path}' is empty")
        
        # Extract latest writing (first revision in file, since latest is at top)
        latest_writing = self._extract_latest_writing(history_content)
        
        if not latest_writing:
            raise ValueError(f"No valid writing found in '{writinghistory_file_path}'")
        
        # Generate to-do list using AI
        todo_list = self._generate_todo_list_with_ai(heuristics_content, latest_writing)
        
        # Read existing to-do list history if output file exists
        todo_history = []
        if os.path.exists(output_file_path):
            try:
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                    # Parse existing history
                    todo_history = self._parse_todo_history(existing_content)
            except Exception as e:
                print(f"Warning: Failed to read existing todo history: {e}. Starting fresh.")
        
        # Create new entry
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = {
            "timestamp": timestamp,
            "todo_list": todo_list,
            "heuristics_file": heuristics_file_path,
            "writinghistory_file": writinghistory_file_path
        }
        
        # Add new entry at the beginning (latest first)
        todo_history.insert(0, new_entry)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise IOError(f"Failed to create output directory '{output_dir}': {str(e)}")
        
        # Save to-do list history to output file (latest first)
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                for i, entry in enumerate(todo_history):
                    f.write(f"{'=' * 80}\n")
                    f.write(f"TODO LIST #{len(todo_history) - i}\n")
                    f.write(f"Timestamp: {entry['timestamp']}\n")
                    f.write(f"Heuristics File: {entry['heuristics_file']}\n")
                    f.write(f"Writing History File: {entry['writinghistory_file']}\n")
                    f.write(f"{'=' * 80}\n\n")
                    f.write(entry['todo_list'])
                    f.write("\n\n")
        except Exception as e:
            raise IOError(f"Failed to write output file '{output_file_path}': {str(e)}")
        
        result = {
            "latest_writing": latest_writing,
            "heuristics": heuristics_content,
            "todo_list": todo_list,
            "output_file": output_file_path,
            "timestamp": timestamp
        }
        
        self.feedback_history.append(result)
        
        return result
    
    def _parse_todo_history(self, content: str) -> List[Dict]:
        """
        Parse existing to-do list history from output file.
        
        Format:
        ================================================================================
        TODO LIST #N
        Timestamp: ...
        Heuristics File: ...
        Writing History File: ...
        ================================================================================
        
        [to-do list content]
        """
        history = []
        # Split by separator blocks (80 equal signs with newlines)
        pattern = r'={80}\nTODO LIST #(\d+)\nTimestamp:\s*(.+?)\nHeuristics File:\s*(.+?)\nWriting History File:\s*(.+?)\n={80}\n\n(.*?)(?=\n={80}\n|$)'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            todo_num = match.group(1)
            timestamp = match.group(2).strip()
            heuristics_file = match.group(3).strip()
            writinghistory_file = match.group(4).strip()
            todo_content = match.group(5).strip()
            
            if todo_content:
                history.append({
                    "todo_num": todo_num,
                    "timestamp": timestamp,
                    "heuristics_file": heuristics_file,
                    "writinghistory_file": writinghistory_file,
                    "todo_list": todo_content
                })
        
        return history
    
    def get_latest_todo_list(self, todo_history_file_path: str) -> str:
        """
        Extract the latest to-do list from history file.
        
        Args:
            todo_history_file_path: Path to to-do list history file
        
        Returns:
            Latest to-do list content
        """
        if not os.path.exists(todo_history_file_path):
            raise FileNotFoundError(f"Todo history file not found: {todo_history_file_path}")
        
        try:
            with open(todo_history_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read todo history file '{todo_history_file_path}': {str(e)}")
        
        # Extract latest (first in file)
        latest_data = self._extract_latest_todo_list(content)
        return latest_data.get("todo_list", "") if latest_data else ""
    
    def _extract_latest_todo_list(self, content: str) -> Dict:
        """
        Extract the latest to-do list from history content.
        
        Returns:
            Dictionary with 'todo_list', 'timestamp', 'heuristics_file', 'writinghistory_file'
        """
        # Find the first todo list block (latest is at top)
        pattern = r'={80}\nTODO LIST #(\d+)\nTimestamp:\s*(.+?)\nHeuristics File:\s*(.+?)\nWriting History File:\s*(.+?)\n={80}\n\n(.*?)(?=\n={80}\n|$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            todo_num = match.group(1)
            timestamp = match.group(2).strip()
            heuristics_file = match.group(3).strip()
            writinghistory_file = match.group(4).strip()
            todo_list = match.group(5).strip()
            
            return {
                "todo_num": todo_num,
                "timestamp": timestamp,
                "heuristics_file": heuristics_file,
                "writinghistory_file": writinghistory_file,
                "todo_list": todo_list
            }
        
        return {}
    
    def _extract_latest_writing(self, history_content: str) -> str:
        """
        Extract the latest writing from history file.
        Latest revision is at the top of the file.
        
        Format:
        ================================================================================
        REVISION #N
        Timestamp: ...
        Ideas File: ...
        Template File: ...
        ================================================================================
        
        [text content]
        """
        # Find the first revision block (latest is at top)
        pattern = r'={80}\n(?:REVISION #\d+\n.*?\n)={80}\n\n(.*?)(?=\n={80}\n|$)'
        match = re.search(pattern, history_content, re.DOTALL)
        
        if match:
            latest_text = match.group(1).strip()
            return latest_text
        
        # Fallback: try to find any content after first separator
        lines = history_content.split('\n')
        in_content = False
        content_lines = []
        
        for line in lines:
            if line.strip() == '=' * 80:
                if not in_content:
                    in_content = True
                    continue
                else:
                    break
            if in_content:
                # Skip metadata lines
                if not any(marker in line for marker in ['REVISION #', 'Timestamp:', 'Ideas File:', 'Template File:']):
                    content_lines.append(line)
        
        if content_lines:
            return '\n'.join(content_lines).strip()
        
        return ""
    
    def _generate_todo_list_with_ai(self, heuristics: str, writing: str) -> str:
        """
        Generate actionable to-do list using AI API based on heuristics and writing.
        
        Args:
            heuristics: Heuristics content
            writing: Latest writing to review
            
        Returns:
            Generated to-do list
        """
        if self.api_provider == "gemini":
            return self._generate_todo_with_gemini(heuristics, writing)
        elif self.api_provider == "openai":
            return self._generate_todo_with_openai(heuristics, writing)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _generate_todo_with_gemini(self, heuristics: str, writing: str) -> str:
        """Generate to-do list using Google Gen AI SDK (Gemini API)."""
        prompt = f"""You are a professor providing feedback on a research paper draft. Based on the evaluation heuristics and the student's writing, generate an actionable to-do list.

EVALUATION HEURISTICS (use these as criteria):
{heuristics}

STUDENT'S LATEST WRITING (review this text):
{writing}

INSTRUCTIONS:
1. Carefully review the student's writing against the provided heuristics
2. Identify specific areas that need improvement
3. Generate an actionable to-do list with clear, specific tasks
4. Format as a PLAIN TEXT numbered list (NOT LaTeX, NOT markdown, just plain text)
5. Use simple formatting:
   - Number items like: 1. First item, 2. Second item, etc.
   - Use plain text only (no LaTeX commands, no markdown, no HTML)
   - Use simple line breaks between items
6. Each item should be:
   - Specific and concrete (not vague)
   - Actionable (the student can directly work on it)
   - Prioritized (more important issues first)
   - Include brief explanations where helpful
7. Focus on the most critical improvements first
8. Be constructive and clear
9. Output ONLY plain text - no formatting codes, no LaTeX, no special characters for formatting

Generate the to-do list in PLAIN TEXT format now:"""

        try:
            response = self.api_model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                todo_list = response.text.strip()
                # Clean up any LaTeX or markdown that might have slipped through
                todo_list = self._clean_todo_list_format(todo_list)
                return todo_list
            else:
                raise ValueError("Empty response from Gemini API")
        except Exception as e:
            raise RuntimeError(f"Error calling Gemini API: {str(e)}")
    
    def _generate_todo_with_openai(self, heuristics: str, writing: str) -> str:
        """Generate to-do list using OpenAI API."""
        prompt = f"""You are a professor providing feedback on a research paper draft. Based on the evaluation heuristics and the student's writing, generate an actionable to-do list.

EVALUATION HEURISTICS (use these as criteria):
{heuristics}

STUDENT'S LATEST WRITING (review this text):
{writing}

INSTRUCTIONS:
1. Carefully review the student's writing against the provided heuristics
2. Identify specific areas that need improvement
3. Generate an actionable to-do list with clear, specific tasks
4. Format as a PLAIN TEXT numbered list (NOT LaTeX, NOT markdown, just plain text)
5. Use simple formatting:
   - Number items like: 1. First item, 2. Second item, etc.
   - Use plain text only (no LaTeX commands, no markdown, no HTML)
   - Use simple line breaks between items
6. Each item should be:
   - Specific and concrete (not vague)
   - Actionable (the student can directly work on it)
   - Prioritized (more important issues first)
   - Include brief explanations where helpful
7. Focus on the most critical improvements first
8. Be constructive and clear
9. Output ONLY plain text - no formatting codes, no LaTeX, no special characters for formatting

Generate the to-do list in PLAIN TEXT format now:"""

        try:
            response = self.api_model.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert professor providing constructive feedback on academic writing. Always generate clear, actionable to-do lists in PLAIN TEXT format only (no LaTeX, no markdown, no formatting codes)."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            if response and response.choices:
                todo_list = response.choices[0].message.content.strip()
                # Clean up any LaTeX or markdown that might have slipped through
                todo_list = self._clean_todo_list_format(todo_list)
                return todo_list
            else:
                raise ValueError("Empty response from OpenAI API")
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")
    
    def _clean_todo_list_format(self, text: str) -> str:
        """
        Clean up LaTeX and markdown formatting from to-do list to ensure plain text.
        
        Args:
            text: Text that may contain LaTeX or markdown formatting
            
        Returns:
            Plain text with formatting removed
        """
        # Remove LaTeX enumerate/itemize environments but keep content
        # Extract content from enumerate/itemize
        def replace_enumerate(match):
            content = match.group(1)
            # Replace \item with numbered items
            items = re.findall(r'\\item\s*(.+?)(?=\\item|\\end\{enumerate\}|\\end\{itemize\}|$)', content, re.DOTALL)
            result = []
            for i, item in enumerate(items, 1):
                cleaned_item = item.strip()
                # Clean nested formatting from item (need to escape backslashes properly)
                cleaned_item = re.sub(r'\\textbf\{([^}]+)\}', r'\1', cleaned_item)
                cleaned_item = re.sub(r'\\textit\{([^}]+)\}', r'\1', cleaned_item)
                cleaned_item = re.sub(r'\\emph\{([^}]+)\}', r'\1', cleaned_item)
                cleaned_item = re.sub(r'\\textcolor\{[^}]+\}\{([^}]+)\}', r'\1', cleaned_item)
                # Remove remaining LaTeX commands (more aggressive)
                cleaned_item = re.sub(r'\\[a-zA-Z]+\*?(\{[^}]*\})?', '', cleaned_item)
                # Clean up any remaining braces
                cleaned_item = re.sub(r'\{([^}]+)\}', r'\1', cleaned_item)
                cleaned_item = cleaned_item.strip()
                result.append(f"{i}. {cleaned_item}")
            return '\n'.join(result)
        
        text = re.sub(r'\\begin\{enumerate\}.*?\[.*?\].*?\n(.*?)\\end\{enumerate\}', replace_enumerate, text, flags=re.DOTALL)
        text = re.sub(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', replace_enumerate, text, flags=re.DOTALL)
        text = re.sub(r'\\begin\{itemize\}(.*?)\\end\{itemize\}', replace_enumerate, text, flags=re.DOTALL)
        
        # Remove standalone LaTeX item commands and convert to numbered list
        items = re.findall(r'\\item\s*(.+?)(?=\\item|$)', text, flags=re.DOTALL)
        if items and len(items) > 0:
            result = []
            for i, item in enumerate(items, 1):
                cleaned = item.strip()
                # Clean formatting
                cleaned = re.sub(r'\\textbf\{([^}]+)\}', r'\1', cleaned)
                cleaned = re.sub(r'\\textit\{([^}]+)\}', r'\1', cleaned)
                cleaned = re.sub(r'\\emph\{([^}]+)\}', r'\1', cleaned)
                cleaned = re.sub(r'\\textcolor\{[^}]+\}\{([^}]+)\}', r'\1', cleaned)
                cleaned = re.sub(r'\\[a-zA-Z]+\{?[^}]*\}?', '', cleaned)  # Remove other LaTeX commands
                result.append(f"{i}. {cleaned}")
            text = '\n'.join(result)
        else:
            # Remove LaTeX item commands inline
            text = re.sub(r'\\item\s*', '\n', text)
        
        # Remove LaTeX formatting commands (if not already removed) - apply multiple passes
        for _ in range(3):  # Multiple passes to handle nested commands
            text = re.sub(r'\\textbf\{([^}]+)\}', r'\1', text)
            text = re.sub(r'\\textit\{([^}]+)\}', r'\1', text)
            text = re.sub(r'\\emph\{([^}]+)\}', r'\1', text)
            text = re.sub(r'\\textcolor\{[^}]+\}\{([^}]+)\}', r'\1', text)
            text = re.sub(r'\\[a-zA-Z]+\*?(\{[^}]*\})?', '', text)  # Remove other LaTeX commands
            # Clean up orphaned braces
            text = re.sub(r'\{([^}]+)\}', r'\1', text)
        
        # Remove LaTeX labels and options
        text = re.sub(r'\[label=[^\]]+\]', '', text)
        text = re.sub(r'\\arabic\*', '', text)
        text = re.sub(r'\\arabic\{enumii\}', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'#+\s*', '', text)
        
        # Clean up extra whitespace and normalize
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r' \n', '\n', text)  # Remove trailing spaces before newlines
        
        return text.strip()

