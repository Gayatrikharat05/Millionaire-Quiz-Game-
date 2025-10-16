import time
import threading
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Available themes
themes = [
    "Science", "Movies", "Sports", "History", "Geography",
    "Chhatrapati Shivaji Maharaj", "Chhatrapati Sambhaji Maharaj"
]

# Keep track of asked questions
if "history_questions" not in st.session_state:
    st.session_state.history_questions = {theme: [] for theme in themes}

# Game state
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "q_count" not in st.session_state:
    st.session_state.q_count = 0
if "question_data" not in st.session_state:
    st.session_state.question_data = None
if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = None

# Functions to generate question and answer
def generate_question(selected_theme):
    prompt = f"""
You are a quiz generator. Create ONE easy multiple-choice trivia question
STRICTLY about: {selected_theme}.
It MUST be factual and relevant to the theme.

Do NOT repeat any of these past questions: {st.session_state.history_questions[selected_theme]}

Output EXACTLY in this format (no extra text, no explanations):

Question: <question text>
Options:
1. <option1>
2. <option2>
3. <option3>
4. <option4>
"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a trivia quiz generator that follows format strictly."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192",
        temperature=0.7
    )

    result = chat_completion.choices[0].message.content.strip()
    
    # Extract question text only for history
    first_line = result.split("\n")[0].replace("Question:", "").strip()
    st.session_state.history_questions[selected_theme].append(first_line)
    
    return result


def generate_answer(question):
    prompt = f"""Please answer this question: {question}
    Output only the correct option number (1-4). No extra text."""
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a trivia quiz answerer."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192"
    )
    return int(chat_completion.choices[0].message.content.strip())

# UI starts here
st.title("💰 Millionaire Quiz Game")

# Step 1: Theme selection
if not st.session_state.selected_theme:
    st.session_state.selected_theme = st.selectbox("Choose a theme", themes)
    if st.button("Start Quiz"):
        st.session_state.score = 0
        st.session_state.q_count = 0
        st.session_state.history_questions = {theme: [] for theme in themes}
        st.rerun()
else:
    # Step 2: Generate new question if needed
    if st.session_state.q_count < 5:
        if not st.session_state.question_data:
            q_data = generate_question(st.session_state.selected_theme)
            # st.session_state.history_questions[st.session_state.selected_theme].append(q_data)
            correct = generate_answer(q_data)
            st.session_state.question_data = q_data
            st.session_state.correct_answer = correct

        # Parse question and options
        lines = st.session_state.question_data.split("\n")
        question_text = lines[0].replace("Question:", "").strip()
        options = [line.split(". ", 1)[1] for line in lines if line.strip().startswith(("1.", "2.", "3.", "4."))]

        st.subheader(f"Question {st.session_state.q_count+1}: {question_text}")
        st.subheader(f"Current Score : {st.session_state.score}")
        choice = st.radio("Select your answer:", options)

        if st.button("Submit"):
            chosen_index = options.index(choice) + 1
            if chosen_index == st.session_state.correct_answer:
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Wrong! Correct answer: {options[st.session_state.correct_answer - 1]}")
            st.session_state.q_count += 1
            st.session_state.question_data = None
            time.sleep(1)
            st.rerun()
    else:
        st.success(f"🎯 Game Over! Your score: {st.session_state.score}/5")
        if st.button("Play Again"):
            st.session_state.selected_theme = None
            st.rerun()
