import os
from dotenv import load_dotenv
from groq import Groq

print("Loading environment...")

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("API key loaded:", bool(api_key))

if not api_key:
    print("ERROR: GROQ_API_KEY was not found in .env")
    raise SystemExit(1)

client = Groq(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Career Planner AI Mentor, "
                    "a helpful educational career assistant. "
                    "Give clear, practical and concise answers."
                )
            },
            {
                "role": "user",
                "content": "Hello! Introduce yourself in two sentences."
            }
        ],
        temperature=0.7,
        max_tokens=300
    )

    print()
    print("===================================")
    print("GROQ SUCCESS")
    print("===================================")
    print()
    print(response.choices[0].message.content)

except Exception as e:

    print()
    print("===================================")
    print("GROQ ERROR")
    print("===================================")
    print()
    print(repr(e))