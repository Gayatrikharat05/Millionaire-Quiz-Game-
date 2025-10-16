import time
import threading

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Available themes
themes = ["Science", "Movies", "Sports", "History", "Geography", 
          "Chhatrapati Shivaji Maharaj", "Chhatrapati Sambhaji Maharaj"]

# history_questions = []
# Initialize history for each theme
history_questions = {theme: [] for theme in themes}


def generate_question(selected_theme):
    prompt = f"""Generate one easy multiple-choice trivia question on the theme '{selected_theme}'. Take care that you don't repeat the question in {history_questions[selected_theme]}.
    Do not give anything else than question and its options. No headings and greetings required
    Output format:
    Question: <text>
    Options:
    1. <option1>
    2. <option2>
    3. <option3>
    4. <option4>
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a trivia quiz generator."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192"
    )
    generate_question = chat_completion.choices[0].message.content
    return generate_question

def generate_answer(question):
    prompt = f"""Please answer this question = {question}
    output format:
    <1-4>
    
    Do not give anything else than the option number of correct answer. I want only the option number
    
    For example, if 2nd option is correct then reply with '2' only
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a trivia quiz answerer."},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192"
    )

    correct_answer = chat_completion.choices[0].message.content
    return correct_answer


# Shared variables
time_limit = 20
user_answer = None
time_up = False
stop_timer = False

def countdown():
    global time_up
    for t in range(time_limit, 0, -1):
        if stop_timer:  # stop counting if answer given
            return
        print(f"⏳ Time left: {t} seconds", end='\r', flush=True)
        time.sleep(1)
    # print("I AM HERE")
    time_up = True
    print("\n⏰ Time's up!")


def get_answer():
    global user_answer, stop_timer
    try:
        ans = input("\nEnter your answer (1-4): ")
        if not time_up:
            stop_timer = True  # stop the countdown when user answers
            if ans.strip().isdigit():
                user_answer = int(ans)
        else:
            user_answer = None
    except:
        user_answer = None

# Game logic
question_count=1
while True:
    question_count+=1
    print("Available themes:")
    for idx, theme in enumerate(themes, start=1):
        print(f"{idx}. {theme}")

    selected_theme = ""
    theme_choice = input("Choose a theme by entering its number: ").strip()
    if theme_choice.isdigit() and 1 <= int(theme_choice) <= len(themes):
        selected_theme = themes[int(theme_choice)-1]
        print(f"\nYou selected: {selected_theme}\n")
    else:
        print("Invalid choice, defaulting to 'Science'")
        selected_theme = "Science"
        print(f"\nYou selected: {selected_theme}\n")

    winnings = 0
    for i in range(5):  # for example, 5 questions
    # Reset variables for new question
        user_answer = None
        time_up = False
        stop_timer = False  # important
    
    print(selected_theme)
    generated_question = generate_question(selected_theme)
    if generated_question:
        history_questions[selected_theme].append(generated_question)
    
    correct_answer =int(generate_answer(generated_question))

    #user_answer = None
    #time_up = False
     # Parse the question to get correct_answer

# print("\n--------------------------------")
    print(f"Question {i+1}")
# print(question[0:-10])
    print("\n--------------------------------")
    print(generated_question)
    print("\n--------------------------------")
    
    # Start timer in parallel
    timer_thread = threading.Thread(target=countdown)
    timer_thread.start()
    
    # <<< change: start input in a separate thread (so timer can stop it)
    input_thread = threading.Thread(target=get_answer)
    input_thread.start()

    # Wait for timer to finish
    timer_thread.join()
    input_thread.join()
    
     # Check the answer
    if time_up and user_answer is None:
        print("❌ You ran out of time!")
        print(f"You won ₹{winnings}.")
        play_again = input("\nDo you want to play again? (y/n): ").strip().lower()
        if play_again != "y":
            exit()  # Stop everything
        else:
            break  # just exit silently
    elif user_answer == correct_answer:
        print("✅ Correct Answer!")
        winnings += 1000
    else:
        print(f"❌ Wrong Answer! The correct answer was {correct_answer}.")
        print(f"You won ₹{winnings}.")    


        play_again = input("\nDo you want to play again? (y/n): ").strip().lower()
        if play_again != "y":
          exit()  # Stop everything
        else:
            break  # just exit silently
