from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def evaluate_answers(quiz, user_answers):

    prompt = f"""
    Evaluate the following quiz answers.

    Quiz:
    {quiz}

    User Answers:
    {user_answers}

    Return:
    - Score out of 100
    - Correct answers
    - Weak areas
    - Improvement suggestions
    """

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_API_MODEL"),
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content