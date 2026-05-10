from openai import OpenAI
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()

# Read API key from .env
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_API_MODEL")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)


def explain_topic(topic, learning_style="visual"):
    """
    Explain topic in different learning styles:
    - visual: Use diagrams, flowcharts, visual descriptions
    - auditory: Step-by-step verbal explanation
    - kinesthetic: Interactive examples and hands-on approaches
    """
    
    if learning_style == "visual":
        prompt = f"""
        Explain this topic in a VISUAL way suitable for visual learners.
        
        Topic: {topic}
        
        Include:
        - ASCII diagrams or visual descriptions
        - Color and structure descriptions
        - Spatial relationships
        - Visual metaphors and comparisons
        - Where applicable: "Draw [something]" suggestions
        """
    
    elif learning_style == "auditory":
        prompt = f"""
        Explain this topic in a STEP-BY-STEP VERBAL way suitable for auditory learners.
        
        Topic: {topic}
        
        Include:
        - Clear numbered steps
        - Spoken-friendly language (conversational tone)
        - Rhythm and patterns
        - Repetition of key concepts
        - Sound-based metaphors ("think of it like...")
        - Dialogue-style explanations
        """
    
    elif learning_style == "kinesthetic":
        prompt = f"""
        Explain this topic in a HANDS-ON, INTERACTIVE way suitable for kinesthetic learners.
        
        Topic: {topic}
        
        Include:
        - Practical examples you can try
        - Step-by-step activities
        - Movement-based descriptions
        - Real-world applications
        - "Try this" activities
        - Tangible, concrete examples
        - Problem-solving approaches
        """
    
    else:  # default
        prompt = f"""
        Explain this topic comprehensively.

        Topic:
        {topic}

        Also include:
        - Easy explanation
        - Real-world example
        - Summary
        """

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def explain_with_multiple_styles(topic):
    """Generate explanations in all three learning styles"""
    
    explanations = {
        "visual": explain_topic(topic, "visual"),
        "auditory": explain_topic(topic, "auditory"),
        "kinesthetic": explain_topic(topic, "kinesthetic")
    }
    
    return explanations