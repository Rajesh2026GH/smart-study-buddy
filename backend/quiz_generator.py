from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Read API key
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_API_MODEL")
# Initialize client
client = OpenAI(api_key=api_key)


def generate_quiz(text, difficulty="medium", learning_style="visual"):
    """
    Generate quiz based on difficulty and learning style
    
    difficulty: easy, medium, hard
    learning_style: visual, auditory, kinesthetic
    """

    if learning_style == "visual":
        quiz_type = "Create visual and diagram-based questions"
    elif learning_style == "auditory":
        quiz_type = "Create step-by-step and narrative-based questions"
    elif learning_style == "kinesthetic":
        quiz_type = "Create practical and scenario-based questions"
    else:
        quiz_type = "Create standard multiple choice questions"

    prompt = f"""
    Generate 5 multiple choice quiz questions from the following content.
    
    Difficulty Level: {difficulty}
    Question Style: {quiz_type}

    Content:
    {text}

    For each question provide:
    1. Question text
    2. Four options (A, B, C, D)
    3. Correct answer
    4. Explanation of why it's correct
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


def generate_varied_quizzes(text):
    """Generate quizzes in all difficulty levels and styles"""
    
    difficulties = ["easy", "medium", "hard"]
    styles = ["visual", "auditory", "kinesthetic"]
    
    quizzes = {}
    for difficulty in difficulties:
        quizzes[difficulty] = {}
        for style in styles:
            quizzes[difficulty][style] = generate_quiz(text, difficulty, style)
    
    return quizzes