import streamlit as st
import pandas as pd
from pymongo import MongoClient
from andi_scores import (
    andi_empfehlungen_deutsch,
    andi_werte_deutsch,
    food_names_deutsch,
)
from datetime import datetime, timedelta, date
import calendar

############### Helper functions ###############

st.set_page_config("Tracker", ":avocado:")

st.markdown(
    """
<style>
.dataframe td, .dataframe th {
    border: none !important;
}
</style>
""",
    unsafe_allow_html=True,
)

current_date = datetime.now()
current_month = calendar.month_name[current_date.month]


def get_current_week():
    # Get the Monday before or on the provided date
    monday = current_date - timedelta(days=current_date.weekday())
    
    # Get the Sunday after the provided date
    sunday = monday + timedelta(days=6)
    
    # Get the desired format "31.07 - 06.08"
    week_format = f"{monday.strftime('%d.%m')} - {sunday.strftime('%d.%m')}"
    
    # Return the week as a tuple (year, week number) and the desired formatted string
    return (current_date.year, current_date.isocalendar()[1], week_format)


current_year, current_week, current_week_format = get_current_week()

############### Database         ###############

# Set up the connection to MongoDB
client = MongoClient(st.secrets["mongo_uri"])
db = client.Cluster0
collection = db.tracker



def add_selected_food_to_db(selected_foods):
    # Create a filter for current year and week
    week_filter = {"year": current_year, "week_number": current_week}
    
    # Check if the entry for the current week exists
    if not collection.find_one(week_filter):
        # If not, initialize an empty entry for the current week
        week_data = {
            "year": current_year,
            "week_number": current_week,
            "foods": {}
        }
        collection.insert_one(week_data)
    
    # Update the food counts for the current week
    for food in selected_foods:
        food_update = {"$inc": {"foods." + food: 1}}
        collection.update_one(week_filter, food_update)

def get_food_log():
    # Query to retrieve the singular data from DB
    data = collection.find_one({})
    if data and "food_log" in data:
        print(f'food_log: {data["food_log"]}')
        return data["food_log"]
    return {}

def get_weekly_summary():
    week_data = collection.find_one({"year": current_year, "week_number": current_week})
    if week_data and "foods" in week_data:
        return week_data["foods"]
    return {}


def get_dataset():
    # Lebensmittel aus der Datenbank filtern und in Kategorien einordnen
    categorized_foods = {}
    category_counts = {}

    for food, count in weekly_data.items():
        for category, foods_in_category in andi_werte_deutsch.items():
            if food in foods_in_category:
                if category not in categorized_foods:
                    categorized_foods[category] = []
                categorized_foods[category].append(food)

                # Summe der Counts für jede Kategorie
                if category not in category_counts:
                    category_counts[category] = 0
                category_counts[category] += count
                break

    total_count = sum(category_counts.values())

    # Daten für DataFrame erstellen
    data = {
        "Kategorie": [],
        "Foods": [],
        "Status": [],
        "Prozentsatz": []
    }

    for category, foods in categorized_foods.items():
        data["Kategorie"].append(category)
        data["Foods"].append(", ".join(foods))
        data["Status"].append(category_counts[category])
        percentage = (category_counts[category] / total_count) * 100
        data["Prozentsatz"].append(round(percentage, 2))

    return pd.DataFrame(data)

# Empfehlungen für Kategorien erstellen
kategorie_help_texts = {}
for category, details in andi_empfehlungen_deutsch.items():
    min_value = details["prozentsatz"].get("minimum", None)
    max_value = details["prozentsatz"].get("maximum", None)
    notiz = details.get("notiz", "")
    
    help_text = []
    if min_value is not None:
        help_text.append(f"Min. {min_value}")
    if max_value is not None:
        help_text.append(f"Max. {max_value}")
    
    help_text.append(notiz)
    kategorie_help_texts[category] = ", ".join(help_text)

#print(kategorie_help_texts)
column_configuration = {
    "Kategorie": st.column_config.TextColumn(
        "Kategorie", max_chars=100, help=kategorie_help_texts
    ),
    "Foods": st.column_config.TextColumn(
        "Foods", max_chars=100
    ),
    "Status": st.column_config.ProgressColumn(
        "Status", min_value=0, max_value=30, format="%d"
    ),
    "Prozentsatz": st.column_config.NumberColumn(
        "Prozentsatz",
    )
}




############### Frontend         ###############

st.header("Food Tracker")
st.text(str(current_week) +" Woche: "+ str(current_week_format))
weekly_data = get_weekly_summary()
different_foods_eaten = len(weekly_data) if weekly_data else 0
progress_percentage = different_foods_eaten / 30
st.progress(progress_percentage,text=f":first_place_medal: {different_foods_eaten} von 30 verschiedenen Foods pro Woche :first_place_medal:")

# Ansicht der wöchentlichen Foods
if weekly_data:
    st.data_editor(
        get_dataset(),
        column_config=column_configuration,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
    )

# st.markdown("-----")

food_selectbox = st.multiselect(
    label="Lebensmittel hinzufügen",
    options=food_names_deutsch,
    key="food_select",
    label_visibility="hidden",
    placeholder="Lebensmittel hinzufügen",
)

# new_food = st.text_input("Neues hinzufügen",label_visibility="hidden",placeholder="Neues hinzufügen")
# if new_food:
#     food_names_deutsch.append(new_food)
#     food_selectbox = st.multiselect(
#         label="Lebensmittel hinzufügen",
#         options=food_names_deutsch,
#         key="food_select_new",
#         label_visibility="hidden",
#         placeholder="Neues hinzufügen",
#     )


options = st.text(f"Auswahl: {food_selectbox}")

if st.button("Speichern"):
    add_selected_food_to_db(food_selectbox)
    st.success("Erfolgreich zur Datenbank hinzugefügt!")
    st.experimental_rerun()



## TODO: This is an awesome multiselect with dropdown 
# import streamlit  as st

# from st_ant_tree import st_ant_tree

# #Example Data with some html code
# tree_data = [
#   {
#     "value": "parent 1",
#     "title": """Test <i>  <b style="color:green"> parent HTML</b></i> test""",
#     "children": [
#       {
#         "value": "parent 1-0",
#         "title": "parent 1-0",
#         "children": [
#           {
#             "value": "leaf1",
#             "title": "leaf1",
#           },
#           {
#             "value": "leaf2",
#             "title": "leaf2",
#           },
#         ],
#       },
#       {
#         "value": "parent 1-1",
#         "title": "parent 1-1",
#         "children": [
#           {
#             "value": "leaf3",
#             "title": """<i> <b style="color:green">leaf3</b> </i>""",
#           },
#         ],
#       },
#     ],
#   },
# ]

# value = st_ant_tree(treeData=tree_data, allowClear= True, bordered= True, max_height= 400, filterTreeNode= True, 
# multiple= True, placeholder= "Choose an option", showArrow= True, showSearch= True, treeCheckable= True,
# width_dropdown= "40%", disabled= False, maxTagCount=5, onChange=alert("Value changed"))



######## Buttons next to each other
# pip install st_btn_select
# Usage
# Creating a Button Selection is really easy.

# from st_btn_select import st_btn_select

# selection = st_btn_select(('option 1', 'option 2', 'option 3'))
# st.write('selection')