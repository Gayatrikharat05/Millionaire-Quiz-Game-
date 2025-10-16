import streamlit as st
import time
import random
import os
import re
from dotenv import load_dotenv
import pandas as pd
from groq import Groq

# --- Setup Groq API ---
load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    st.error("❌ Missing GROQ_API_KEY in .env file. Please add it before running.")
    st.stop()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- Quiz Themes ---
themes = ["Bollywood", "General Knowledge", "IPL", "Chhatrapati Shivaji Maharaj", "History"]

# --- Session State Initialization ---
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
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
if "lifelines" not in st.session_state:
    st.session_state.lifelines = {"50-50": True, "Skip": True, "Hint": True}
if "shuffled_options" not in st.session_state:
    st.session_state.shuffled_options = None
if "options_50_50" not in st.session_state:
    st.session_state.options_50_50 = None
if "history_questions" not in st.session_state:
    st.session_state.history_questions = {theme: [] for theme in themes}

# --- Helper Functions ---
def generate_question(theme, difficulty="Easy"):
    prompt = f"""
    You are a quiz generator. Create ONE easy multiple-choice question
    STRICTLY about: {theme}.
    It MUST be factual and relevant to the theme.
    Do NOT repeat these questions: {st.session_state.history_questions[theme]}

    Output exactly in this format:
    Question: <question>
    Options:
    1. <option1>
    2. <option2>
    3. <option3>
    4. <option4>
    Explanation: <short explanation>
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a strict trivia question generator."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()
    first_line = content.split("\n")[0].replace("Question:", "").strip()
    st.session_state.history_questions[theme].append(first_line)
    return content


def generate_answer(question):
    prompt = f"Answer this question: {question}\nOutput only the correct option number (1-4)."
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a trivia answerer."},
            {"role": "user", "content": prompt},
        ],
        model="llama-3.1-8b-instant"
    )
    content = response.choices[0].message.content.strip()
    match = re.search(r'[1-4]', content)
    return int(match.group()) if match else random.randint(1, 4)


def load_highscores():
    if os.path.exists("highscores.csv"):
        return pd.read_csv("highscores.csv")
    return pd.DataFrame(columns=["Name", "Score"])


def save_highscore(name, score):
    df = load_highscores()
    df = pd.concat([df, pd.DataFrame([{"Name": name, "Score": score}])], ignore_index=True)
    df.to_csv("highscores.csv", index=False)


def reset_game():
    st.session_state.selected_theme = None
    st.session_state.score = 0
    st.session_state.q_count = 0
    st.session_state.question_data = None
    st.session_state.correct_answer = None
    st.session_state.lifelines = {"50-50": True, "Skip": True, "Hint": True}
    st.session_state.shuffled_options = None
    st.session_state.options_50_50 = None
    st.session_state.history_questions = {theme: [] for theme in themes}

# --- Streamlit UI ---
st.title("💰 Millionaire Quiz - Next Level")

# --- Player Name ---
if not st.session_state.player_name:
    name_input = st.text_input("Enter your name to start the game:")
    if st.button("Confirm Name") and name_input.strip():
        st.session_state.player_name = name_input.strip()
        st.rerun()
else:
    st.write(f"Welcome, **{st.session_state.player_name}**! 🎮")

    # --- Theme Selection ---
    if st.session_state.selected_theme is None:
        selected = st.selectbox("🎯 Choose a theme:", themes)
        if st.button("Start Quiz"):
            st.session_state.selected_theme = selected
            st.session_state.score = 0
            st.session_state.q_count = 0
            st.session_state.question_data = None
            st.session_state.correct_answer = None
            st.session_state.lifelines = {"50-50": True, "Skip": True, "Hint": True}
            st.session_state.shuffled_options = None
            st.session_state.options_50_50 = None
            st.rerun()
    else:
        st.write(f"📘 Current Theme: **{st.session_state.selected_theme}**")

        # --- Quiz Completed ---
        if st.session_state.q_count >= 5:
            st.success(f"🏆 Quiz Completed! Final Score: {st.session_state.score}/5")
            save_highscore(st.session_state.player_name, st.session_state.score)
            st.dataframe(load_highscores())

            if st.button("Play Again"):
                reset_game()
                st.rerun()

        else:
            # --- Generate Question if Needed ---
            if not st.session_state.question_data:
                q_data = generate_question(st.session_state.selected_theme)
                correct = generate_answer(q_data)
                st.session_state.question_data = q_data
                st.session_state.correct_answer = correct

                lines = q_data.split("\n")
                options = [line.split(". ", 1)[1] for line in lines if line.strip().startswith(("1.", "2.", "3.", "4."))]
                st.session_state.original_options = options.copy()
                random.shuffle(options)
                st.session_state.shuffled_options = options
                correct_text = st.session_state.original_options[correct - 1]
                st.session_state.correct_shuffled = options.index(correct_text)
                st.session_state.options_50_50 = options.copy()

            # --- Display Question ---
            lines = st.session_state.question_data.split("\n")
            question_text = lines[0].replace("Question:", "").strip()
            explanation_lines = [line.replace("Explanation:", "").strip() for line in lines if "Explanation:" in line]
            explanation = explanation_lines[0] if explanation_lines else "No explanation available."

            options_list = st.session_state.shuffled_options
            correct_index = st.session_state.correct_shuffled

            st.subheader(f"Question {st.session_state.q_count+1}: {question_text}")
            st.subheader(f"Score: {st.session_state.score}/5")

            # --- Lifelines ---
            col1, col2, col3 = st.columns(3)

            if st.session_state.lifelines["50-50"]:
                if col1.button("50-50", key=f"fifty_{st.session_state.q_count}"):
                    correct_opt = options_list[correct_index]
                    wrong_opts = [opt for opt in options_list if opt != correct_opt]
                    remove_opts = random.sample(wrong_opts, 2)
                    st.session_state.options_50_50 = [opt for opt in options_list if opt not in remove_opts]
                    st.session_state.lifelines["50-50"] = False
            else:
                col1.button("50-50", disabled=True, key=f"fifty_disabled_{st.session_state.q_count}")

            if st.session_state.lifelines["Skip"]:
                if col2.button("Skip", key=f"skip_{st.session_state.q_count}"):
                    st.session_state.q_count += 1
                    st.session_state.question_data = None
                    st.session_state.shuffled_options = None
                    st.session_state.options_50_50 = None
                    st.session_state.lifelines["Skip"] = False
                    st.rerun()
            else:
                col2.button("Skip", disabled=True, key=f"skip_disabled_{st.session_state.q_count}")

            if st.session_state.lifelines["Hint"]:
                if col3.button("Hint", key=f"hint_{st.session_state.q_count}"):
                    st.info(f"💡 Hint: {explanation.split('.')[0]}...")
                    st.session_state.lifelines["Hint"] = False
            else:
                col3.button("Hint", disabled=True, key=f"hint_disabled_{st.session_state.q_count}")

            # --- Answer Options ---
            choice = st.radio("Select your answer:", st.session_state.options_50_50, key=f"radio_{st.session_state.q_count}")

            # --- Submit ---
            if st.button("Submit", key=f"submit_{st.session_state.q_count}"):
                if choice == options_list[correct_index]:
                    st.success("✅ Correct!")
                    st.session_state.score += 1
                    st.balloons()
                else:
                    st.error(f"❌ Wrong! Correct answer: {options_list[correct_index]}")
                    st.info(f"Explanation: {explanation}")

                st.session_state.q_count += 1
                st.session_state.question_data = None
                st.session_state.shuffled_options = None
                st.session_state.options_50_50 = None
                time.sleep(1)
                st.rerun()
