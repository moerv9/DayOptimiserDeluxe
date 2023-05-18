import streamlit as st
import pandas as pd
import numpy as np
import datetime
import emoji
from pymongo import MongoClient
from streamlit import components

# Custom CSS for dark background with gradient
custom_css = """
<style>
    body {
        background: rgb(2,0,36);
        background: linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(9,9,121,1) 35%, rgba(0,212,255,1) 100%);
    }
    .stTextInput>div>div>input {
        color: #ffffff;
    }
    .stTextArea>div>div>textarea {
        color: #ffffff;
    }
</style>
"""

# Add custom CSS to the dashboard
components.v1.html(custom_css, height=0)
#st.markdown(custom_css, unsafe_allow_html=True)

# MongoDB connection
client = MongoClient(st.secrets["mongo_uri"])
db = client.Cluster0
time_audit_records_col = db.timeAuditRecords
priority_tasks_col = db.tasks

# Helper function to find or create a daily entry
def find_or_create_daily_entry(date):
    daily_entry = time_audit_records_col.find_one({"date": date})

    if not daily_entry:
        daily_entry = {
            "date": date,
            "time_records": [],
            "thoughts": ""
        }
        result = time_audit_records_col.insert_one(daily_entry)
        daily_entry["_id"] = result.inserted_id

    return daily_entry


# Time Audit Record Section
st.title("Time Audit Record")

date = datetime.date.today().strftime("%d %b")
#date_col1,time_col1 = st.columns(2)
current_time = datetime.datetime.now()
current_hour = datetime.datetime.now().hour + 1
previous_hour = (current_hour - 1) % 24
time_frame = f"{previous_hour} - {current_hour}"
st.text(f"Timestamp: {date}, {time_frame}")# date = st.date_input("", value=datetime.date.today())
#time_col1 = st.time_input("Time: ", value=current_time,step=datetime.timedelta(minutes=60),label_visibility="hidden")

emojis = [
    emoji.emojize(":bulb:"),
    emoji.emojize(":runner:"),
    emoji.emojize(":person_in_lotus_position:"),
    emoji.emojize(":sleeping:"),
    emoji.emojize(":family:"),
    emoji.emojize(":hamburger:"),
    emoji.emojize(":coffee:"),
    emoji.emojize(":tv:"),
    emoji.emojize(":iphone:"),
    emoji.emojize(":books:"),
    emoji.emojize(":notes:"),
]
# Custom CSS for selected emoji button
# selected_button_css = """
# <style>
#     .selected-emoji {
#         border-bottom: 2px solid #ffffff;
#     }
# </style>
# """

# st.markdown(selected_button_css, unsafe_allow_html=True)

emoji_columns = st.columns(len(emojis))
selected_emoji = st.session_state.get("selected_emoji", None)

for idx, emoji_symbol in enumerate(emojis):
    if emoji_columns[idx].button(emoji_symbol, key=emoji_symbol, help="Click to select this emoji"):
        selected_emoji = emoji_symbol
        st.session_state.selected_emoji = selected_emoji

    if selected_emoji == emoji_symbol:
        emoji_columns[idx].markdown(f'<span class="selected-emoji">{emoji_symbol}</span>', unsafe_allow_html=True)


#st.markdown("## Enter your activity")
#selected_time = col1.time_input(f"{date}", value=datetime.datetime.now().time(),step=datetime.timedelta(minutes=60),label_visibility="visible")
user_input = st.text_input("Enter activity description", value="", max_chars=None, key=None, type="default")

# st.markdown("## Or choose from default activities:")
# activity = st.selectbox("Select an activity", list(default_activities.values()))


submit = st.button("Submit Time Record")

if submit:
    if user_input:
        activity = user_input

    record = {
        "activity": activity,
        "emoji": selected_emoji,
        "date": date,
        "time": time_frame,
    }

    daily_entry = find_or_create_daily_entry(date)
    time_audit_records_col.update_one({"_id": daily_entry["_id"]}, {"$push": {"time_records": record}})

    st.success("Time record added successfully!")


########################## Second Brain Section ###############################
# Divider
st.markdown("---")

# Second Brain Section
st.markdown("## Second Brain :brain:")
thoughts = st.text_area("Enter your random thoughts here...", height=None, max_chars=None, key=None)

# Save Thoughts button
save_thoughts = st.button("Save Thoughts")
if save_thoughts:
    date = datetime.date.today()
    daily_entry = find_or_create_daily_entry(date)
    time_audit_records_col.update_one({"_id": daily_entry["_id"]}, {"$set": {"thoughts": thoughts}})

    st.success("Thoughts saved successfully!")


########################## Task Priority Management Section ###############################


# Divider
st.markdown("---")

# Task Priority Management Section
st.markdown("## Task Priority Management: I.C.E")

# Instruction manual
st.markdown(
    """
    <details>
    <summary style="cursor:pointer;font-weight:bold;color:#ffffff">I.C.E Method Instructions</summary>
    <p>
        The I.C.E. method helps prioritize tasks by scoring them based on Impact, Confidence, and Ease.
    </p>
    <ul>
        <li>1 - 20 points for how Impactful they are</li>
        <li>1 - 10 points for how Confident you are in your ability to complete</li>
        <li>1 - 5 points for how Easy they are to complete</li>
    </ul>
    <p>
        Total score determines the priority:
        <ul>
            <li>28 - 35: High</li>
            <li>20 - 28: Medium</li>
            <li>Less than 20: Low</li>
        </ul>
    </p>
    </details>
    """,
    unsafe_allow_html=True
)

# Task input
task = st.text_input("Task:", value="", max_chars=None, key=None, type="default")

# I.C.E. inputs
impact = st.slider("Impact (1-20):", min_value=1, max_value=20, value=1, step=1)
confidence = st.slider("Confidence (1-10):", min_value=1, max_value=10, value=1, step=1)
ease = st.slider("Ease (1-5):", min_value=1, max_value=5, value=1, step=1)

# Calculate the total score
total_score = impact + confidence + ease

# Color-code the total score
if total_score >= 28:
    priority_color = "green"
    priority = "High"
elif total_score >= 20:
    priority_color = "orange"
    priority = "Medium"
else:
    priority_color = "red"
    priority = "Low"


# Load existing tasks
existing_tasks = list(priority_tasks_col.find())
task_data = []

for task in existing_tasks:
    task_id = task["_id"]
    completed = task.get("completed")
    task_name = task["task"]
    impact = task["impact"]
    confidence = task["confidence"]
    ease = task["ease"]
    total_score = impact + confidence + ease

    # Color-code the total score
    if total_score >= 28:
        priority_color = "green"
        priority = "High"
    elif total_score >= 20:
        priority_color = "orange"
        priority = "Medium"
    else:
        priority_color = "red"
        priority = "Low"

    task_data.append({"id": task_id,"completed":completed, "task": task_name, "impact": impact, "confidence": confidence, "ease": ease, "total_score": f'<span style="color:{priority_color};font-weight:bold;">{total_score} ({priority})</span>'})

task_df = pd.DataFrame(task_data)

# def on_delete_task(task_id):
#     priority_tasks_col.delete_one({"_id": task_id})
#     st.experimental_rerun()

# delete_buttons = []
# for _, row in task_df.iterrows():
#     task_id = row["id"]
#     delete_buttons.append(st.button("Delete", key=task_id, on_click=on_delete_task, args=(task_id,)))

# task_df["delete"] = delete_buttons

def on_task_toggle(task_id, value):
    priority_tasks_col.update_one({"_id": task_id}, {"$set": {"completed": value}})
    st.experimental_rerun()

# Create a column for checkboxes and another for the task table
checkbox_col, task_col = st.columns([1, 4])

# Render checkboxes in the first column
for _, row in task_df.iterrows():
    task_id = row["id"]
    completed = row["completed"]
    with checkbox_col:
        st.checkbox("Completed", value=completed, key=task_id, on_change=on_task_toggle, args=(task_id,))

# Hide the 'completed' column from the task table and display it in the second column
task_df = task_df.drop(columns=["completed"])
task_col.write(task_df.drop(columns=["id"]).to_html(escape=False, index=False), unsafe_allow_html=True)


save_task = st.button("Save Task")

#html_table = task_df.to_html(escape=False, index=False)
# Add a style tag to the table HTML to hide the first column
# html_table = html_table.replace('<table border="1" class="dataframe">', '<table border="1" class="dataframe"><style>table.dataframe th:nth-child(1), table.dataframe td:nth-child(1) {display: none;}</style>')

# # Render the modified HTML table in Streamlit
# st.write(html_table, unsafe_allow_html=True)
# Save task button

if save_task:
    new_task = {
        "task": task,
        "impact": impact,
        "confidence": confidence,
        "ease": ease,
        "completed": completed,
    }
    priority_tasks_col.insert_one(new_task)
    st.experimental_rerun()


# Display the table
# table_data = pd.DataFrame(
#     {
#         "Task": [task],
#         "Impact": [impact],
#         "Confidence": [confidence],
#         "Ease": [ease],
#         "Total Score": [f'<span style="color:{priority_color};font-weight:bold;">{total_score} ({priority})</span>'],
#     }
# )

# st.write(table_data.to_html(escape=False, index=False), unsafe_allow_html=True)
