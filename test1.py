import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_question():
    prompt = """Generate one multiple-choice trivia question.
    Output format:
    Question: <text>
    Options:
    1. <option1>
    2. <option2>
    3. <option3>
    4. <option4>
    Correct: <number 1-4>"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a trivia quiz generator."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192"
    )

    return chat_completion.choices[0].message.content

if __name__ == "__main__":
    print(generate_question())
