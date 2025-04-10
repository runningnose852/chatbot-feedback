import streamlit as st
import openai
import pandas as pd
import gspread
from google.oauth2 import service_account

# Setup authorized client
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)
client_gsheets = gspread.authorize(creds)

# ✅ Open sheet by key instead of by name
SHEET_ID = "your_actual_sheet_id_here"  # Replace this with your sheet's ID
sheet = client_gsheets.open_by_key("1_udeJGkY6jpKibc0J9Z6LfSX33v86xYurme9yGgIFno").sheet1

from openai import OpenAI

# === Configuration ===
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

# === Load Rubric from File ===
with open("rubric.txt", "r", encoding="utf-8") as f:
    rubric_text = f.read()

# === Streamlit UI Setup ===
st.set_page_config(page_title="📚 EssayPal")
st.title("📚 EssayPal")

# === Session State ===
if "answers" not in st.session_state:
    st.session_state.answers = []

# === Student Submission Form ===
with st.form("submission_form"):
    name = st.text_input("Your Name")
    topic = st.text_input("Topic")
    student_answer = st.text_area("Your Answer")
    submitted = st.form_submit_button("Submit")

word_count = len(student_answer.split())
max_words = 200  # Changed to 200 words
# Display word count
st.caption(f"Word count: {word_count}/{max_words}")

# Check word limit during submission
if submitted:
    if word_count > max_words:
        st.error(f"Please limit your answer to {max_words} words. Current count: {word_count}")
    elif name and student_answer:  # Only process if we have both name and answer
        # Display a spinner while generating feedback
        with st.spinner('Generating personalized feedback... Please wait.'):
            prompt = f"""
You are talking to the student as an assistant te
