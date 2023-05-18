import streamlit as st
import streamlit.components.v1 as components
from pymongo import MongoClient
import hashlib
import matplotlib.pyplot as plt
import pandas as pd
import emoji, random

client = MongoClient(st.secrets["mongo_uri"])
db = client.Cluster0
collection = db.genre_selection_cols


def generate_device_fingerprint():
    # Generate device fingerprint using relevant attributes
    user_agent = st.experimental_get_query_params().get("user_agent", [""])[0]
    ip_address = st.experimental_get_query_params().get("client_ip", [""])[0]
    fingerprint = hashlib.sha256((user_agent + ip_address).encode()).hexdigest()
    return fingerprint

emojis = ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼","🐊","🐎","🐅","🐍","🐒","🐣","🐧"]


# def ChangeButtonColour(widget_label, font_color, background_color):
#     font_color = str(font_color).strip("()")
#     # background_color = str(background_color).strip("()")
#     print(background_color)
#     htmlstr = f"""
#         <script>
#             var elements = window.parent.document.querySelectorAll('button');
#             for (var i = 0; i < elements.length; ++i) {{ 
#                 if (elements[i].innerText == '{widget_label}') {{ 
#                     elements[i].style.color ='rgba{str(font_color)}';
#                     elements[i].style.background = 'rgba{str(background_color)}'
#                 }}
#             }}
#         </script>
#         """
#     # components.html(f"{htmlstr}", height=0, width=0)
#     st.markdown(htmlstr, unsafe_allow_html=True)
    
color_map = plt.colormaps["Set2"]



def main():
    st.title("Welche Genres willst du hören?")
    genres = [
        "Drum and Bass",
        "Techno",
        "House",
        "EDM",
        "Pop",
        "Rock",
        "Trance",
        "2000s",
        "90s",
        "80s",
        "Country",
        "Grime",
        "Rap",
        "Hip Hop"
    ]

    # Create a session state to keep track of the selected genres
    if "selected_genres" not in st.session_state:
        st.session_state.selected_genres = []

    # Generate the device fingerprint
    device_fingerprint = generate_device_fingerprint()


    columns_per_row = 3  # Number of columns per row
    num_genres = len(genres)
    num_rows = num_genres // columns_per_row  # Number of rows needed

    # Adjust the number of rows if not evenly divisible by columns_per_row
    if num_genres % columns_per_row != 0:
        num_rows += 1

    # Split genres into groups of columns_per_row
    genre_groups = [genres[i:i+columns_per_row] for i in range(0, num_genres, columns_per_row)]

    # Display buttons in columns
    for group in genre_groups:
        cols = st.columns(columns_per_row)
        for col, genre in zip(cols, group):
            button_id = f"{genre}_button"
            if col.button(genre, key=button_id):
                # Toggle the selected genre in the session state
                if genre in st.session_state.selected_genres:
                    st.session_state.selected_genres.remove(genre)
                else:
                    st.session_state.selected_genres.append(genre)

    # for i, genre in enumerate(genres):
    #     button_id = f"{genre}_button"

    #     # Check if the button is clicked
    #     if st.button(genre, key=button_id):
    #         # Toggle the selected genre in the session state
    #         if genre in st.session_state.selected_genres:
    #             st.session_state.selected_genres.remove(genre)
    #         else:
    #             st.session_state.selected_genres.append(genre)

    # Display the selected genres
    selected_genres_str = ", ".join(st.session_state.selected_genres)
    st.markdown(f"**Selected Genres: {selected_genres_str}**", unsafe_allow_html=True)

    if st.button("Submit",type="primary"):
        selected_genres = st.session_state.selected_genres

        existing_entry = collection.find_one({"fingerprint": device_fingerprint})

        if existing_entry:
            st.warning("You have already submitted genres.")
        else:
            # Save the new genres and device fingerprint to MongoDB collection
            entry = {"fingerprint": device_fingerprint, "genres": selected_genres}
            collection.insert_one(entry)
            st.success("Genres submitted successfully!")


    st.markdown("---")
    st.empty()

    st.header("Was sagt die Meute?")
    # Retrieve the data from the MongoDB collection
    all_entries = collection.find({})
    all_genres = [entry["genres"] for entry in all_entries]
    if len(all_genres) == 0:
        st.warning("Keine Daten bisher.")
        return
    else:
        flattened_genres = [genre for sublist in all_genres for genre in sublist]
        # Create a dataframe to count the genres
        genre_counts = pd.Series(flattened_genres).value_counts()
        # Plot the genre count diagram
        #plt.pie(genre_counts, labels=genres, autopct='%1.1f%%', colors=color_map(range(len(genre_counts))))
        #genre_counts.plot(kind="bar", color=color_map(range(len(genre_counts))))
        plt.figure(figsize=(10, 6),facecolor='white')
        genre_counts.plot(kind="pie", labels=genre_counts.index, autopct='%1.1f%%', colors=color_map(range(len(genre_counts))))
        plt.title(None)
        plt.ylabel(None)
        plt.xlabel(None)
        st.pyplot(plt)

    # cols = st.columns(4)
    # cols[0].button('first button', key='b1')
    # cols[1].button('second button', key='b2')
    # cols[2].button('third button', key='b3')
    # cols[3].button('fourth button', key='b4')

    # ChangeButtonColour('House', 'red', 'blue') # button txt to find, colour to assign red for text blue background
    # ChangeButtonColour('fourth button', '#c19af5', '#354b75') # button txt to find, colour to assign
    st.markdown("---")
    st.empty()
    st.header("Gib mir deinen Senf")
    user_text = st.text_area(label="💭",placeholder="Schreibst du hier...")
    if st.button("Save"):
        existing_entry = collection.find_one({"fingerprint": device_fingerprint})
        if existing_entry:
            existing_entry.setdefault("mein_senf", []).append(user_text)
            collection.update_one({"fingerprint": device_fingerprint}, {"$set": existing_entry})
            st.success("Text updated successfully!")
        else:
            entry = {"fingerprint": device_fingerprint, "mein_senf": [user_text]}
            collection.insert_one(entry)
            st.success("Text saved successfully!")
        user_text = ""


    # Display all entries from MongoDB
    st.header("Logbuch:")
    all_entries = collection.find({})
    all_senf = [entry["mein_senf"] for entry in all_entries]
    if len(all_senf) == 0:
        st.warning("Keine Daten bisher.")
        return
    else:
        senf = [senf for sublist in all_senf for senf in sublist]
        for entry in senf:
            st.write(f"{random.choice(emojis)} {entry}")



if __name__ == "__main__":
    main()
