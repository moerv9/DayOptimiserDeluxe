import streamlit as st
import pandas as pd
from pymongo import MongoClient
from andi_scores import andi_empfehlungen_deutsch, andi_werte_deutsch, food_names_deutsch
from datetime import datetime, timedelta,date
import calendar
import emoji

############### Helper functions ###############
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


def get_current_week(date):
    # Get the Monday before or on the provided date
    monday = date - timedelta(days=date.weekday())
    # Get the Sunday after the provided date
    sunday = monday + timedelta(days=6)
    # Return the week as a string in the 'day-month' format
    return monday.strftime('%d-%m') + '-' + sunday.strftime('%d-%m')

############### Database         ###############

# Set up the connection to MongoDB
client = MongoClient(st.secrets["mongo_uri"])
db = client.Cluster0
collection = db.tracker


def add_selected_food_to_db(user, selected_food):
    # Get current date and month
    current_date = datetime.now()
    current_month = calendar.month_name[current_date.month]
    current_week = get_current_week(current_date)
    
    # Query to check if a document for the user and current month exists
    query = {'user': user, 'food_log.' + current_month: {'$exists': True}}
    user_month_doc = collection.find_one(query)
    
    # If such a document exists, update it
    if user_month_doc:
        # Update query to increment the count of the selected food in the current week
        update_query = {'$inc': {'food_log.' + current_month + '.' + current_week + '.' + selected_food: 1}}
        collection.update_one(query, update_query)
    else:
        # If no such document exists, create a new one
        new_doc = {
            'user': user,
            'food_log': {
                current_month: {
                    current_week: {
                        selected_food: 1
                    }
                }
            }
        }
        collection.insert_one(new_doc)



############### Frontend         ###############

st.title("Food Tracker")
if 'username' not in st.session_state:
    st.session_state.username = st.text_input("Username")
else:
    username = st.session_state.username
date = date.today().strftime("%d %b")
st.text(date)

food_selectbox = st.multiselect("Choose a food", food_names_deutsch, key='food_select')

options = st.text(food_selectbox)

if st.button("Add to DB"):
    add_selected_food_to_db(username, food_selectbox)



