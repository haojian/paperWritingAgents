"""
Test script for Style Analyzer Agent
Tests semantic analysis and template generation.
"""

from style_analyzer import StyleAnalyzerAgent

def test_style_analyzer():
    """Test the style analyzer with a sample section."""
    
    # Initialize analyzer with Google Gen AI SDK (new API)
    # Make sure to set GEMINI_API_KEY environment variable or pass the key
    # Install with: pip install google-genai
    analyzer = StyleAnalyzerAgent(
        name="Test Analyzer",
        api_provider="gemini",
        gemini_api_key=None  # Will use GEMINI_API_KEY env variable if not provided
    )
    
    # Sample introduction section
    sample_section = """
    Machine learning has revolutionized healthcare in recent years. 
    However, current methods still face significant challenges in clinical decision-making.
    Existing approaches often lack interpretability, which is crucial for medical applications.
    For example, deep learning models are frequently criticized as "black boxes" that fail to provide explanations for their predictions.
    This limitation becomes critical when medical professionals need to understand why a particular diagnosis or treatment recommendation was made.
    Therefore, there is an urgent need for interpretable machine learning methods in healthcare.
    In this paper, we propose a novel approach that combines the accuracy of deep learning with the interpretability of traditional rule-based systems.
    """
    
    print("=" * 60)
    print("STYLE ANALYZER TEST")
    print("=" * 60)
    print("\nAnalyzing section...")
    print("\nInput text:")
    print(sample_section)
    print("\n" + "-" * 60)
    
    try:
        result = analyzer.analyze_section(sample_section, section_name="Introduction")
        
        print("\n✓ Analysis Complete!\n")
        
        print("SENTENCE ANALYSIS:")
        print("-" * 60)
        for i, sent_analysis in enumerate(result["sentences"]):
            print(f"\nSentence {i + 1}:")
            print(f"  Text: {sent_analysis.get('text', '')[:100]}...")
            print(f"  Role: {sent_analysis.get('role', 'unknown')}")
            print(f"  Key Concepts: {', '.join(sent_analysis.get('key_concepts', []))}")
            if sent_analysis.get('transition_type'):
                print(f"  Transition: {sent_analysis.get('transition_type')} - {sent_analysis.get('transition_description', '')}")
        
        print("\n\nTRANSITIONS:")
        print("-" * 60)
        for transition in result["transitions"]:
            print(f"\nSentence {transition['from_sentence'] + 1} → Sentence {transition['to_sentence'] + 1}:")
            print(f"  Type: {transition.get('transition_type', 'N/A')}")
            print(f"  Description: {transition.get('transition_description', 'N/A')}")
            print(f"  Flow: [{transition.get('from_role', 'N/A')}] → [{transition.get('to_role', 'N/A')}]")
        
        print("\n\nSEMI-STRUCTURED TEMPLATE:")
        print("-" * 60)
        print(result["template"])
        
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure to:")
        print("  1. Install Google Gen AI SDK: pip install google-genai")
        print("  2. Set GEMINI_API_KEY environment variable: export GEMINI_API_KEY='your_key'")
        print("  3. Or pass gemini_api_key parameter when creating StyleAnalyzerAgent")
        print("  4. Get API key from: https://makersuite.google.com/app/apikey")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_style_analyzer()

