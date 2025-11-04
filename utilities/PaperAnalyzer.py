"""
Paper Analyzer Utility
Analyzes PDF files and generates template files.
Saves annotation files to PaperAnalysis folder.
"""

import os
from pathlib import Path
from typing import Optional, Dict
from style_analyzer import StyleAnalyzerAgent


class PaperAnalyzer:
    """Utility to analyze papers and generate templates."""
    
    def __init__(self, output_base_dir: str = "PaperAnalysis",
                 api_provider: str = "gemini",
                 gemini_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        """
        Initialize PaperAnalyzer utility.
        
        Args:
            output_base_dir: Base directory for analysis files (default: "PaperAnalysis")
            api_provider: "gemini" or "openai" (default: "gemini")
            gemini_api_key: Optional Gemini API key
            openai_api_key: Optional OpenAI API key
        """
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(exist_ok=True)
        
        self.analyzer = StyleAnalyzerAgent(
            name="Paper Analyzer",
            api_provider=api_provider,
            gemini_api_key=gemini_api_key,
            openai_api_key=openai_api_key
        )
    
    def analyze_section(self, section_text: str, section_name: str, 
                       paper_name: Optional[str] = None) -> Dict:
        """
        Analyze a section of text and generate template.
        
        Args:
            section_text: Text content of the section
            section_name: Name of the section (e.g., "Introduction")
            paper_name: Name of the paper (for saving annotation)
            
        Returns:
            Analysis result dictionary
        """
        # Analyze the section
        result = self.analyzer.analyze_section(section_text, section_name)
        
        # Save annotation if paper_name provided
        if paper_name:
            self._save_annotation(paper_name, section_name, result)
        
        return result
    
    def analyze_file(self, input_file_path: str, section_name: str = "Introduction",
                     paper_name: Optional[str] = None) -> Dict:
        """
        Analyze a text file and generate template.
        
        Args:
            input_file_path: Path to input text file
            section_name: Name of the section
            paper_name: Name of the paper (for saving annotation)
            
        Returns:
            Analysis result dictionary
        """
        # Generate output filename
        if paper_name:
            output_file = self.output_base_dir / f"{paper_name}_{section_name.lower()}_template.txt"
        else:
            output_file = self.output_base_dir / f"{Path(input_file_path).stem}_template.txt"
        
        # Analyze and generate template
        result = self.analyzer.analyze_file_and_generate_template(
            input_file_path=input_file_path,
            output_file_path=str(output_file),
            section_name=section_name
        )
        
        return result
    
    def _save_annotation(self, paper_name: str, section_name: str, analysis: Dict):
        """
        Save annotation to PaperAnalysis folder.
        
        Args:
            paper_name: Name of the paper
            section_name: Name of the section
            analysis: Analysis result dictionary
        """
        annotation_file = self.output_base_dir / f"{paper_name}_{section_name.lower()}_annotation.txt"
        
        with open(annotation_file, 'w', encoding='utf-8') as f:
            f.write(f"===== Paper: {paper_name} =====\n")
            f.write(f"===== Section: {section_name} =====\n\n")
            
            f.write("===== Template =====\n")
            f.write(analysis.get('template', '') + "\n\n")
            
            f.write("===== Sentence Analysis =====\n")
            for i, sent in enumerate(analysis.get('sentences', [])):
                f.write(f"\nSentence {i+1}:\n")
                f.write(f"  Text: {sent.get('text', '')[:100]}...\n")
                f.write(f"  Role: {sent.get('role', 'unknown')}\n")
                if sent.get('key_concepts'):
                    f.write(f"  Key Concepts: {', '.join(sent.get('key_concepts', []))}\n")
            
            f.write("\n===== Transitions =====\n")
            for trans in analysis.get('transitions', []):
                f.write(f"\n{trans.get('from_sentence', 0)+1} → {trans.get('to_sentence', 0)+1}:\n")
                f.write(f"  Type: {trans.get('transition_type', 'N/A')}\n")
                f.write(f"  Description: {trans.get('transition_description', 'N/A')}\n")
        
        print(f"  ✓ Annotation saved: {annotation_file}")


def main():
    """Command-line interface for PaperAnalyzer."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analyze a text file and generate template'
    )
    parser.add_argument('input_file', help='Path to input text file')
    parser.add_argument('--section-name', '-s', default='Introduction',
                       help='Name of the section (default: Introduction)')
    parser.add_argument('--paper-name', '-p', help='Name of the paper')
    parser.add_argument('--provider', default='gemini', choices=['gemini', 'openai'],
                       help='API provider (default: gemini)')
    
    args = parser.parse_args()
    
    # Get API keys
    gemini_key = os.getenv("GEMINI_API_KEY") if args.provider == "gemini" else None
    openai_key = os.getenv("OPENAI_API_KEY") if args.provider == "openai" else None
    
    analyzer = PaperAnalyzer(
        api_provider=args.provider,
        gemini_api_key=gemini_key,
        openai_api_key=openai_key
    )
    
    try:
        analyzer.analyze_file(
            input_file_path=args.input_file,
            section_name=args.section_name,
            paper_name=args.paper_name
        )
        print("✓ Analysis complete!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

