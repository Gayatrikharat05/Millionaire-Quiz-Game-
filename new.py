# question_data = """What is the biggest planet
# 1. Jupyter
# 2. Urenus
# 3. Earth
# 4. Mars"""


# question, opt1, opt2, opt3, opt4 = question_data.split("\n")
# print(question)
# print("---------------------------")
# print(opt1)
# print(opt2)
# print(opt3)
# print(opt4)

import streamlit as st 
name = ["Shubham", "Gayatri"]

st.session_state.name = st.selectbox("Choose your name", name)

st.subheader(st.session_state.name)