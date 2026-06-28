from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def evaluate_answers(quiz, user_answers):
    """
    Evaluate quiz answers using OpenAI and return structured JSON
    
    Returns: {
        "score": int (0-100),
        "total_questions": int,
        "correct_count": int,
        "incorrect_count": int,
        "weak_areas": [str],
        "feedback": str,
        "question_feedback": [
            {"question_num": int, "correct": bool, "explanation": str}
        ]
    }
    """
    
    prompt = f"""
You are an expert quiz evaluator. Evaluate these quiz answers and return ONLY valid JSON (no markdown, no code blocks, no extra text).

QUIZ:
{quiz}

USER ANSWERS:
{user_answers}

Return this JSON structure exactly (NO markdown, NO backticks):
{{
    "score": <integer 0-100>,
    "total_questions": <number of questions in quiz>,
    "correct_count": <number of correct answers>,
    "incorrect_count": <number of wrong answers>,
    "weak_areas": [<list of topics the user struggled with>],
    "feedback": "<overall assessment and encouragement>",
    "question_feedback": [
        {{"question_num": 1, "correct": true, "explanation": "<why this answer is correct>"}},
        {{"question_num": 2, "correct": false, "explanation": "<why this answer is incorrect and what is correct>"}}
    ]
}}

Evaluate fairly and provide constructive feedback. Be strict but fair with scoring.
"""
    
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_API_MODEL", "gpt-3.5-turbo"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    # Extract JSON from response
    response_text = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    # Parse JSON
    try:
        result = json.loads(response_text)
        
        # Validate response has required fields
        required_fields = ["score", "total_questions", "correct_count", 
                          "incorrect_count", "weak_areas", "feedback", "question_feedback"]
        for field in required_fields:
            if field not in result:
                raise ValueError(f"Missing field: {field}")
        
        # Ensure score is integer 0-100
        result["score"] = max(0, min(100, int(result["score"])))
        
        return result
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return error structure
        return {
            "score": 0,
            "total_questions": 0,
            "correct_count": 0,
            "incorrect_count": 0,
            "weak_areas": ["General"],
            "feedback": "Error evaluating answers",
            "error": f"Failed to parse evaluation: {str(e)}",
            "raw_response": response_text,
            "question_feedback": []
        }