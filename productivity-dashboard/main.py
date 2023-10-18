import streamlit as st
from googletrans import Translator
import random

# Greeting Translation
def get_random_greeting():
    greetings = ["Good Morning", "Good Day", "Hello", "Hi"]
    languages = ['es', 'fr', 'de', 'ja', 'zh-cn', 'ko', 'ru', 'ar', 'it', 'pt'] # Spanish, French, etc.

    translator = Translator()
    lang = random.choice(languages)
    translation = translator.translate(random.choice(greetings), dest=lang).text
    return translation, lang

greeting, lang = get_random_greeting()
st.header(greeting)
#if st.button("Listen"):
    # Implement a call to a Text-to-Speech API here. For instance, Google Text-to-Speech API.

# Getting Ready Section
st.subheader("Getting Ready")
prep_tasks = ["Coffee", "No distractions", "Plan the day", "Set priorities", "Clean workspace"]
for task in prep_tasks:
    st.checkbox(task)

# Modified Pomodoro Timer - A placeholder, as Streamlit doesn't natively support this.
st.subheader("Position Reminder")
if st.button("Start Timer"):
    st.write("Timer started. Remember to switch your position every 20 minutes!")

# Time Tracking
st.subheader("Time Tracking")

total_hours = st.slider("Total Work Time", 0, 30, 15)
project_hours = st.slider("Project Work Time", 0, 7, 3)

st.metric("Total Worked Hours", f"{total_hours}/30h")
st.metric("Project Worked Hours", f"{project_hours}/7h")

# Run using `streamlit run filename.py`
