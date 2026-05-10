from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def extract_concepts(text):

    prompt = f"""
    Extract important study concepts from the following text.

    Return only bullet points.

    Text:
    {text}
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