import streamlit as st
from cryptography.fernet import Fernet
import pickle

def load_data(encrypted_data, key):
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    ingredients = pickle.loads(decrypted_data)
    return ingredients

st.title('Decryptor for Wine Tasting Game')

st.write("Please input the encrypted data and the key.")

data_input = st.text_input("Enter your encrypted data")
key_input = st.text_input("Enter your key", type="password")

if data_input and key_input:
    try:
        decrypted_data = load_data(data_input.encode(), key_input.encode())
        st.write("The decrypted data is:")
        for ingredient in decrypted_data:
            st.write(ingredient)
    except:
        st.write("An error occurred during decryption. Please make sure that the data and key are correct.")
