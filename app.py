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
# Divider
st.markdown("---")
st.subheader("👩‍🏫 Teacher Panel (Password Protected)")

# Password input (hidden text)
teacher_pw = st.secrets.get("TEACHER_PASSWORD", None)

with st.expander("🔐 Enter Teacher Password"):
    pw_input = st.text_input("Password", type="password")
    if pw_input and teacher_pw and pw_input == teacher_pw:
        st.success("🔓 Access granted. Viewing teacher panel.")

        if st.session_state.answers:
            df = pd.DataFrame(st.session_state.answers)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download All Feedback", csv, "student_feedback.csv", "text/csv")
    elif pw_input:
        st.error("❌ Incorrect password.")
