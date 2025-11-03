"""
Main Coordinator for Research Paper Writing Agents
Orchestrates interactions between Student Writer, Style Analyzer, and Professor Feedback agents.
"""

from student_writer import StudentWriterAgent
from style_analyzer import StyleAnalyzerAgent
from professor_feedback import ProfessorFeedbackAgent
from typing import List
import json


class PaperWritingCoordinator:
    """Coordinates the multi-agent paper writing process."""
    
    def __init__(self, reference_papers: List[str] = None, gemini_api_key: str = None):
        """
        Initialize the coordinator.
        
        Args:
            reference_papers: Optional list of paths to PDF papers for Style Analyzer to learn from
            gemini_api_key: Optional Gemini API key for deep semantic analysis. 
                           If not provided, will try to get from GEMINI_API_KEY environment variable.
        """
        self.student_writer = StudentWriterAgent("Student Writer")
        # Style Analyzer learns from reference papers first, uses Gemini API if available
        self.style_analyzer = StyleAnalyzerAgent(
            "Style Analyzer", 
            reference_papers=reference_papers,
            gemini_api_key=gemini_api_key
        )
        self.professor = ProfessorFeedbackAgent("Professor Feedback", "General Academic")
        
        if reference_papers:
            print(f"✓ Style Analyzer initialized with {len(reference_papers)} reference paper(s)")
            if self.style_analyzer.style_template:
                print(f"  - Template developed with {len(self.style_analyzer.style_template.get('sections', {}))} section types")
    
    def write_and_review_paper(self, topic: str, sections: List[str] = None, 
                               requirements: dict = None, num_iterations: int = 1):
        """
        Complete workflow: write paper, analyze style, get professor feedback.
        
        Args:
            topic: Research topic
            sections: List of sections to write (default: standard sections)
            requirements: Optional requirements dictionary
            num_iterations: Number of revision iterations
            
        Returns:
            Dictionary containing paper and all feedback
        """
        if sections is None:
            sections = ["Introduction", "Methodology", "Results", "Discussion", "Conclusion"]
        
        if requirements is None:
            requirements = {}
        
        print(f"\n{'='*60}")
        print(f"RESEARCH PAPER WRITING AGENTS SYSTEM")
        print(f"{'='*60}")
        print(f"\nTopic: {topic}")
        print(f"Sections: {', '.join(sections)}")
        
        # Step 1: Student Writer creates the paper
        print(f"\n{'─'*60}")
        print("STEP 1: Student Writer Agent - Drafting Paper...")
        print(f"{'─'*60}")
        paper = self.student_writer.write_full_paper(topic, sections, requirements)
        
        print(f"✓ Paper drafted with {len(paper)} sections")
        for section_name in paper.keys():
            word_count = len(paper[section_name].split())
            print(f"  - {section_name}: {word_count} words")
        
        # Step 2: Style Analyzer reviews the paper (using learned template if available)
        print(f"\n{'─'*60}")
        print("STEP 2: Style Analyzer Agent - Analyzing Style and Quality...")
        print(f"{'─'*60}")
        if self.style_analyzer.style_template:
            print("  (Using template learned from reference papers)")
        style_analysis = self.style_analyzer.analyze_paper(paper, topic)
        
        print(f"✓ Overall Style Score: {style_analysis['overall_score']:.2f}/1.0")
        print(f"  - Strengths identified: {len(style_analysis['strengths'])}")
        print(f"  - Weaknesses identified: {len(style_analysis['weaknesses'])}")
        print(f"  - Style issues found: {len(style_analysis['style_issues'])}")
        
        # Show template compliance if available
        if style_analysis.get('template_compliance'):
            compliance = style_analysis['template_compliance']
            if compliance.get('overall_compliance', 0) > 0:
                print(f"  - Template Compliance: {compliance['overall_compliance']:.2%}")
        
        # Show role analysis if available
        if self.style_analyzer.style_template:
            role_analyses = [sa.get('role_analysis', {}) for sa in style_analysis.get('section_analyses', {}).values() if sa.get('role_analysis')]
            if role_analyses:
                avg_role_compliance = sum(ra.get('role_compliance', {}).get('overall_compliance', 0) for ra in role_analyses) / len(role_analyses) if role_analyses else 0
                if avg_role_compliance > 0:
                    print(f"  - Role Structure Compliance: {avg_role_compliance:.2%}")
                    print(f"    (Analyzed sentence and paragraph functional roles)")
        
        # Step 3: Professor provides feedback
        print(f"\n{'─'*60}")
        print("STEP 3: Professor Feedback Agent - Providing Academic Review...")
        print(f"{'─'*60}")
        professor_feedback = self.professor.review_paper(paper, topic, style_analysis)
        
        print(f"✓ Professor Review Complete")
        print(f"  - Estimated Grade: {professor_feedback['grade_estimate']}")
        print(f"  - Overall Strengths: {len(professor_feedback['strengths'])}")
        print(f"  - Overall Weaknesses: {len(professor_feedback['weaknesses'])}")
        print(f"  - Improvement Suggestions: {len(professor_feedback['suggestions_for_improvement'])}")
        
        # Iterative revision if requested
        for iteration in range(1, num_iterations + 1):
            if iteration > 1:
                print(f"\n{'─'*60}")
                print(f"REVISION ITERATION {iteration}...")
                print(f"{'─'*60}")
                
                # Student revises based on feedback
                revised_paper = {}
                for section_name, content in paper.items():
                    section_feedback = professor_feedback['section_feedback'].get(section_name, {})
                    feedback_text = " ".join(section_feedback.get('recommendations', []))
                    revised_paper[section_name] = self.student_writer.revise_section(
                        section_name, content, feedback_text
                    )
                paper = revised_paper
                
                # Re-analyze and get feedback
                style_analysis = self.style_analyzer.analyze_paper(paper, topic)
                professor_feedback = self.professor.review_paper(paper, topic, style_analysis)
                
                print(f"✓ Revision {iteration} complete")
                print(f"  - Updated Style Score: {style_analysis['overall_score']:.2f}/1.0")
                print(f"  - Updated Grade: {professor_feedback['grade_estimate']}")
        
        return {
            "paper": paper,
            "style_analysis": style_analysis,
            "professor_feedback": professor_feedback,
            "topic": topic
        }
    
    def print_detailed_report(self, results: dict):
        """Print a detailed report of all agent outputs."""
        print(f"\n{'='*60}")
        print("DETAILED REPORT")
        print(f"{'='*60}")
        
        # Paper content
        print(f"\n📄 PAPER CONTENT:")
        print(f"{'─'*60}")
        for section_name, content in results["paper"].items():
            print(f"\n{section_name}:")
            print(content[:300] + "..." if len(content) > 300 else content)
        
        # Style Analysis
        print(f"\n\n📊 STYLE ANALYSIS:")
        print(f"{'─'*60}")
        analysis = results["style_analysis"]
        print(f"Overall Score: {analysis['overall_score']:.2f}/1.0")
        
        print(f"\nStrengths:")
        for strength in analysis['strengths'][:5]:  # Show first 5
            print(f"  ✓ {strength}")
        
        print(f"\nWeaknesses:")
        for weakness in analysis['weaknesses'][:5]:  # Show first 5
            print(f"  ✗ {weakness}")
        
        print(f"\nStyle Issues:")
        for issue in analysis['style_issues'][:5]:  # Show first 5
            print(f"  ⚠ {issue}")
        
        print(f"\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  → {rec}")
        
        # Professor Feedback
        print(f"\n\n👨‍🏫 PROFESSOR FEEDBACK:")
        print(f"{'─'*60}")
        feedback = results["professor_feedback"]
        print(f"\nOverall Assessment:")
        print(f"  {feedback['overall_assessment']}")
        
        print(f"\nEstimated Grade: {feedback['grade_estimate']}")
        
        print(f"\nStrengths:")
        for strength in feedback['strengths']:
            print(f"  ✓ {strength}")
        
        print(f"\nWeaknesses:")
        for weakness in feedback['weaknesses']:
            print(f"  ✗ {weakness}")
        
        print(f"\nSuggestions for Improvement:")
        for suggestion in feedback['suggestions_for_improvement']:
            print(f"  → {suggestion}")
        
        print(f"\nSpecific Comments:")
        for comment in feedback['specific_comments']:
            print(f"  • {comment}")
        
        print(f"\n{'='*60}\n")


def main():
    """Example usage of the research paper writing agents."""
    # Option 1: Initialize without reference papers (original behavior)
    # coordinator = PaperWritingCoordinator()
    
    # Option 2: Initialize with reference papers for Style Analyzer to learn from
    # Uncomment and specify paths to your PDF papers:
    # reference_papers = [
    #     "path/to/reference_paper1.pdf",
    #     "path/to/reference_paper2.pdf",
    # ]
    # coordinator = PaperWritingCoordinator(reference_papers=reference_papers)
    
    # Option 3: Initialize with Gemini API key for deep semantic analysis
    # You can provide the API key directly or set GEMINI_API_KEY environment variable:
    # coordinator = PaperWritingCoordinator(gemini_api_key="your_api_key_here")
    # Or set environment variable: export GEMINI_API_KEY="your_api_key_here"
    
    coordinator = PaperWritingCoordinator()
    
    # Example: Write a paper on a specific topic
    topic = "Machine Learning Applications in Healthcare"
    sections = ["Introduction", "Methodology", "Results", "Discussion", "Conclusion"]
    
    results = coordinator.write_and_review_paper(
        topic=topic,
        sections=sections,
        requirements={"length": "medium"},
        num_iterations=1
    )
    
    # Print detailed report
    coordinator.print_detailed_report(results)
    
    # Save results to JSON file
    output_file = "paper_results.json"
    with open(output_file, 'w') as f:
        # Convert results to JSON-serializable format
        json_results = {
            "topic": results["topic"],
            "paper": results["paper"],
            "style_analysis": results["style_analysis"],
            "professor_feedback": results["professor_feedback"]
        }
        json.dump(json_results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")


if __name__ == "__main__":
    main()

