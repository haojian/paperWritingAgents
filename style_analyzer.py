"""

example: python analyze_and_generate_template.py "citesee-intro.txt" "template.txt"

Style Analyzer Agent
Analyzes research paper sections for semantic roles, transitions, and structure.
Generates semi-structured templates based on AI-powered semantic analysis.
"""

from typing import Dict, List, Optional, Tuple
import re
import os
import json

# Try to import Google Gen AI SDK (new API)
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


class StyleAnalyzerAgent:
    """Agent that analyzes paper style and generates templates."""
    
    def __init__(self, name: str = "Style Analyzer", 
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize Style Analyzer Agent.
        
        Args:
            name: Name of the agent
            api_provider: AI API provider to use ("gemini" or "openai")
            gemini_api_key: Optional Gemini API key. If not provided, will try GEMINI_API_KEY env variable.
            openai_api_key: Optional OpenAI API key. If not provided, will try OPENAI_API_KEY env variable.
        """
        self.name = name
        self.api_provider = api_provider.lower()
        self.analysis_history = []
        
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
            # Create client using new Google Gen AI SDK
            self.api_model = GenAIClient(api_key=self.api_key)
            self.api_available = True
            print(f"✓ Google Gen AI SDK configured for semantic analysis")
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
            print(f"✓ OpenAI API configured for semantic analysis")
        except Exception as e:
            print(f"Warning: Failed to configure OpenAI API: {str(e)}")
            self.api_available = False
    
    def analyze_section(self, section_text: str, section_name: Optional[str] = None) -> Dict:
        """
        Analyze a section of text for semantic roles and transitions.
        Generates a semi-structured template based on the analysis.
        
        Args:
            section_text: The text content of the section
            section_name: Optional name of the section (e.g., "Introduction")
            
        Returns:
            Dictionary containing:
            - sentences: List of analyzed sentences with roles
            - transitions: Transition relationships between sentences
            - template: Semi-structured template string
            - semantic_structure: Detailed semantic analysis
        """
        if not self.api_available:
            raise ValueError(
                f"API ({self.api_provider}) is not available. "
                "Please configure the API key or install the required library."
            )
        
        # Split text into sentences
        sentences = self._split_into_sentences(section_text)
        
        if not sentences:
            return {
                "sentences": [],
                "transitions": [],
                "template": "",
                "semantic_structure": {}
            }
        
        # Analyze semantics and roles using AI API
        semantic_analysis = self._analyze_semantics_with_ai(
            sentences, section_name or "Section"
        )
        
        # Generate semi-structured template
        template = self._generate_template(semantic_analysis)
        
        # Extract transition relationships
        transitions = self._extract_transitions(semantic_analysis)
        
        result = {
            "sentences": semantic_analysis.get("sentence_analyses", []),
            "transitions": transitions,
            "template": template,
            "semantic_structure": semantic_analysis
        }
        
        self.analysis_history.append(result)
        return result
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Split by sentence endings
        sentences = re.split(r'([.!?]+)', text)
        
        # Recombine sentences with their punctuation
        combined = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = (sentences[i] + sentences[i + 1]).strip()
                if sentence:
                    combined.append(sentence)
        
        # If odd number, add last part
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            combined.append(sentences[-1].strip())
        
        return combined
    
    def _analyze_semantics_with_ai(self, sentences: List[str], section_name: str) -> Dict:
        """
        Use AI API to analyze semantics, roles, and transitions of sentences.
        
        Args:
            sentences: List of sentences to analyze
            section_name: Name of the section
            
        Returns:
            Dictionary with semantic analysis results
        """
        if self.api_provider == "gemini":
            return self._analyze_with_gemini(sentences, section_name)
        elif self.api_provider == "openai":
            return self._analyze_with_openai(sentences, section_name)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _analyze_with_gemini(self, sentences: List[str], section_name: str) -> Dict:
        """Analyze using Google Gen AI SDK (new Gemini API)."""
        sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
        
        prompt = f"""Analyze the following sentences from the "{section_name}" section of an academic research paper.

For each sentence, identify:
1. Its semantic role/purpose (e.g., "introduces background", "explains research gap", "presents key idea", "provides example", "explains importance", "defines concepts", "compares approaches", "presents methodology", "discusses results", "concludes points", etc.)
2. Its relationship to previous sentences (transition type: continuation, contrast, example, elaboration, conclusion, etc.)
3. Key concepts or topics it addresses

Sentences:
{sentences_text}

Respond with a JSON object containing:
- "sentence_analyses": Array of objects, one per sentence, each with:
  - "sentence_index": (0-indexed)
  - "text": The sentence text
  - "role": A concise description of the sentence's semantic role (e.g., "brief introduction of the background", "explains why the problem is important", "presents the key novel idea")
  - "transition_type": Relationship to previous sentence (null for first sentence)
  - "transition_description": Description of how it relates to previous sentence
  - "key_concepts": Array of key concepts/topics in this sentence

Example response format:
{{
  "sentence_analyses": [
    {{
      "sentence_index": 0,
      "text": "Machine learning has transformed healthcare.",
      "role": "brief introduction of the background",
      "transition_type": null,
      "transition_description": null,
      "key_concepts": ["machine learning", "healthcare"]
    }},
    {{
      "sentence_index": 1,
      "text": "However, current methods have limitations.",
      "role": "identifies the research gap",
      "transition_type": "contrast",
      "transition_description": "Contrasts the promise with current limitations",
      "key_concepts": ["limitations", "current methods"]
    }}
  ]
}}

Return ONLY valid JSON, nothing else."""

        try:
            # Use new Google Gen AI SDK API
            response = self.api_model.models.generate_content(
                model="gemini-2.5-flash",  # Using latest model
                contents=prompt
            )
            
            if response and hasattr(response, 'text') and response.text:
                # Clean response text
                text = response.text.strip()
                # Remove markdown code blocks if present
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*', '', text)
                text = text.strip()
                
                # Parse JSON
                result = json.loads(text)
                return result
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse Gemini response as JSON: {e}")
            if hasattr(response, 'text'):
                print(f"Response text: {response.text[:500] if response.text else 'None'}")
        except Exception as e:
            print(f"Warning: Error calling Google Gen AI SDK: {e}")
        
        # Return empty structure on error
        return {
            "sentence_analyses": [
                {
                    "sentence_index": i,
                    "text": s,
                    "role": "unknown",
                    "transition_type": None,
                    "transition_description": None,
                    "key_concepts": []
                }
                for i, s in enumerate(sentences)
            ]
        }
    
    def _analyze_with_openai(self, sentences: List[str], section_name: str) -> Dict:
        """Analyze using OpenAI API."""
        sentences_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
        
        prompt = f"""Analyze the following sentences from the "{section_name}" section of an academic research paper.

For each sentence, identify:
1. Its semantic role/purpose (e.g., "introduces background", "explains research gap", "presents key idea", "provides example", "explains importance", "defines concepts", "compares approaches", "presents methodology", "discusses results", "concludes points", etc.)
2. Its relationship to previous sentences (transition type: continuation, contrast, example, elaboration, conclusion, etc.)
3. Key concepts or topics it addresses

Sentences:
{sentences_text}

Respond with a JSON object containing:
- "sentence_analyses": Array of objects, one per sentence, each with:
  - "sentence_index": (0-indexed)
  - "text": The sentence text
  - "role": A concise description of the sentence's semantic role (e.g., "brief introduction of the background", "explains why the problem is important", "presents the key novel idea")
  - "transition_type": Relationship to previous sentence (null for first sentence)
  - "transition_description": Description of how it relates to previous sentence
  - "key_concepts": Array of key concepts/topics in this sentence

Return ONLY valid JSON, nothing else."""

        try:
            response = self.api_model.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in academic writing analysis. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            if response and response.choices:
                text = response.choices[0].message.content.strip()
                # Remove markdown code blocks if present
                text = re.sub(r'```json\s*', '', text)
                text = re.sub(r'```\s*', '', text)
                text = text.strip()
                
                # Parse JSON
                result = json.loads(text)
                return result
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse OpenAI response as JSON: {e}")
        except Exception as e:
            print(f"Warning: Error calling OpenAI API: {e}")
        
        # Return empty structure on error
        return {
            "sentence_analyses": [
                {
                    "sentence_index": i,
                    "text": sentences[i] if i < len(sentences) else "",
                    "role": "unknown",
                    "transition_type": None,
                    "transition_description": None,
                    "key_concepts": []
                }
                for i in range(len(sentences))
            ]
        }
    
    def _generate_template(self, semantic_analysis: Dict) -> str:
        """
        Generate a semi-structured template from semantic analysis.
        
        Template format: [role1]. [role2]. [role3]...
        
        Args:
            semantic_analysis: Semantic analysis dictionary from AI
            
        Returns:
            Semi-structured template string
        """
        sentence_analyses = semantic_analysis.get("sentence_analyses", [])
        
        if not sentence_analyses:
            return ""
        
        # Sort by sentence index
        sorted_analyses = sorted(sentence_analyses, key=lambda x: x.get("sentence_index", 0))
        
        # Extract roles and format as template
        template_parts = []
        for analysis in sorted_analyses:
            role = analysis.get("role", "unknown")
            # Format role in template brackets
            template_parts.append(f"[{role}]")
        
        # Join with ". " to create template
        template = ". ".join(template_parts)
        
        return template
    
    def _extract_transitions(self, semantic_analysis: Dict) -> List[Dict]:
        """
        Extract transition relationships between sentences.
        
        Args:
            semantic_analysis: Semantic analysis dictionary
            
        Returns:
            List of transition dictionaries
        """
        sentence_analyses = semantic_analysis.get("sentence_analyses", [])
        sorted_analyses = sorted(sentence_analyses, key=lambda x: x.get("sentence_index", 0))
        
        transitions = []
        for i in range(1, len(sorted_analyses)):
            prev = sorted_analyses[i - 1]
            curr = sorted_analyses[i]
            
            transition = {
                "from_sentence": prev.get("sentence_index", i - 1),
                "to_sentence": curr.get("sentence_index", i),
                "transition_type": curr.get("transition_type"),
                "transition_description": curr.get("transition_description"),
                "from_role": prev.get("role"),
                "to_role": curr.get("role")
            }
            transitions.append(transition)
        
        return transitions
    
    def analyze_file_and_generate_template(self, input_file_path: str, output_file_path: str, section_name: Optional[str] = None) -> Dict:
        """
        Read a text file, analyze it for semantic roles, and save the template to an output file.
        
        Args:
            input_file_path: Path to the input text file containing the section to analyze
            output_file_path: Path to the output file where the template will be saved
            section_name: Optional name of the section (e.g., "Introduction"). 
                         If not provided, will try to infer from filename or use "Section"
            
        Returns:
            Dictionary containing:
            - sentences: List of analyzed sentences with roles
            - transitions: Transition relationships between sentences
            - template: Semi-structured template string
            - semantic_structure: Detailed semantic analysis
            - input_file: Path to input file
            - output_file: Path to output file
        """
        # Check if input file exists
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
        
        # Read the text file
        try:
            with open(input_file_path, 'r', encoding='utf-8') as f:
                section_text = f.read()
        except Exception as e:
            raise IOError(f"Failed to read input file '{input_file_path}': {str(e)}")
        
        if not section_text.strip():
            raise ValueError(f"Input file '{input_file_path}' is empty")
        
        # Infer section name from filename if not provided
        if not section_name:
            # Extract filename without extension
            base_name = os.path.splitext(os.path.basename(input_file_path))[0]
            # Remove common suffixes like "-intro", "-introduction"
            section_name = re.sub(r'[-_]intro(duction)?$', '', base_name, flags=re.IGNORECASE)
            if not section_name:
                section_name = "Section"
        
        # Analyze the section
        analysis_result = self.analyze_section(section_text, section_name=section_name)
        
        # Extract template
        template = analysis_result.get("template", "")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise IOError(f"Failed to create output directory '{output_dir}': {str(e)}")
        
        # Save template to output file
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(template)
        except Exception as e:
            raise IOError(f"Failed to write output file '{output_file_path}': {str(e)}")
        
        # Add file paths to result
        analysis_result["input_file"] = input_file_path
        analysis_result["output_file"] = output_file_path
        
        return analysis_result
