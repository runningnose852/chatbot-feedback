import streamlit as st
import openai
import pandas as pd
import gspread
from google.oauth2 import service_account
from openai import OpenAI

# === Configuration ===
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

# Google Sheets credentials from Streamlit Secrets
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client_gsheets = gspread.authorize(creds)
try:
    sheet = client_gsheets.open("Chatbot Responses").sheet1
except Exception as e:
    st.error(\"❌ Google Sheets access failed. Please confirm:
    - Sheet name is exactly: 'Chatbot Responses'
    - It is shared with the service account
    - Your credentials are correct

    Error:\n\n\" + str(e))
    st.stop()


# === Load Rubric from File ===
with open("rubric.txt", "r", encoding="utf-8") as f:
    rubric_text = f.read()

# === Streamlit UI Setup ===
st.set_page_config(page_title="📚 In-Class Feedback Chatbot")
st.title("📚 In-Class Feedback Chatbot")

# === Session State ===
if "answers" not in st.session_state:
    st.session_state.answers = []

# === Student Submission Form ===
with st.form("submission_form"):
    name = st.text_input("Your Name")
    student_answer = st.text_area("Your Answer")
    submitted = st.form_submit_button("Submit")

    if submitted and name and student_answer:
        # Generate feedback
        prompt = f"""
You are an assistant teacher. Evaluate the student's answer based on the rubric below.

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

        # Show feedback to student
        st.success("✅ Your answer has been submitted!")
        st.markdown("### 💬 Feedback")
        st.markdown(feedback)

        # Save to session
        st.session_state.answers.append({
            "Name": name,
            "Answer": student_answer,
            "Feedback": feedback
        })

        # Save to Google Sheet
        sheet.append_row([name, student_answer, feedback])

# === Teacher View (Hidden Table & Download) ===
st.markdown("---")
st.subheader("👩‍🏫 Teacher Panel – Review All Responses")

if st.session_state.answers:
    df = pd.DataFrame(st.session_state.answers)
    st.dataframe(df)
