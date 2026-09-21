import streamlit as st
import mysql.connector
conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="Pavi@2050",
    database="sbi"
)
cursor = conn.cursor()
print("Connected Successfully")


import streamlit as st

st.title("Hello Streamlit!")

st.write("This is a simple interactive app.")

name = st.text_input("Enter your name")

if st.button("Greet"):
    st.write(f"Hello, {name}!")
