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
    if submitted:
        if not rubric_text:
            st.warning("Please upload a rubric first.")
        elif name and student_answer:
            st.session_state.answers.append({"name": name, "answer": student_answer})
            st.success("Answer submitted!")

st.markdown("---")
st.subheader("👩‍🏫 Teacher Feedback Panel")

if st.button("Generate Feedback for All"):
    if not rubric_text:
        st.warning("Please upload a rubric first.")
    elif not st.session_state.answers:
        st.warning("No student answers submitted.")
    else:
        st.session_state.results = []  # clear previous
        for item in st.session_state.answers:
    name = item["name"]
    student_answer = item["answer"]

    prompt = f"""
You are an assistant teacher. Your task is to evaluate a student's answer based on a provided rubric and model answer.

📋 Rubric & Model Answer:
{rubric_text}

🧑 Student's Answer:
{student_answer}

✅ Please assess the answer according to the rubric and provide clear, constructive feedback. Mention if the answer is accurate, well-structured, and includes appropriate examples.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    feedback = response.choices[0].message.content

            # Save result
            st.session_state.results.append({
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
