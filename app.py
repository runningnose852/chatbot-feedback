import streamlit as st
import openai
import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from google.oauth2 import service_account

creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)


load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

with open("rubric.txt", "r", encoding="utf-8") as f:
    rubric_text = f.read()

if "answers" not in st.session_state:
    st.session_state.answers = []

if "results" not in st.session_state:
    st.session_state.results = []

st.set_page_config(page_title="📚 In-Class Chatbot with Rubric + CSV")

st.title("📚 In-Class Chatbot with Rubric-Based Feedback")


# Student form
with st.form("submission_form"):
    name = st.text_input("Your Name")
    student_answer = st.text_area("Your Answer")
    submitted = st.form_submit_button("Submit")

    if submitted and name and student_answer:
        # Generate feedback immediately
        prompt = f"""
You are an assistant teacher. Evaluate the following student answer using the rubric and model answer below.

Rubric:
{rubric_text}

Student Answer:
{student_answer}

Provide specific, constructive feedback.
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        feedback = response.choices[0].message.content

        # Save and display feedback
        st.success("✅ Your answer has been submitted!")
        st.markdown("### 💬 Feedback")
        st.markdown(feedback)

        # Optional: store it in session or write to file/Google Sheet
        st.session_state.answers.append({
            "Name": name,
            "Answer": student_answer,
            "Feedback": feedback
        })


st.success("✅ Feedback generated for all students!")

# Show and download results
if st.session_state.results:
    df = pd.DataFrame(st.session_state.results)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Feedback as CSV", csv, "student_feedback.csv", "text/csv")

# Clear all
if st.button("Clear All Data"):
    st.session_state.answers = []
    st.session_state.results = []
    st.success("Session cleared.")
