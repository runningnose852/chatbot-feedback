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

# Calculate word counts
word_count_answer = len(student_answer.split())
word_count_topic = len(topic.split())
max_words_topic = 200   # Word limit for topic
max_words_answer = 500  # Word limit for answer



# Display word counts
st.caption(f"Topic word count: {word_count_topic}/{max_words_topic}")
st.caption(f"Answer word count: {word_count_answer}/{max_words_answer}")


# Check word limits during submission
if submitted:
    if word_count_answer > max_words_answer:
        st.error(f"Please limit your answer to {max_words_answer} words. Current count: {word_count_answer}")
    elif word_count_topic > max_words_topic:
        st.error(f"Please limit your topic to {max_words_topic} words. Current count: {word_count_topic}")
    elif name and student_answer:  # Only process if we have both name and answer
        # Display a spinner while generating feedback
        with st.spinner('Generating personalized feedback... Please wait.'):
            prompt = f"""
You are talking to the student as an assistant teacher helping a student improve their formal argumentative essay. Use simple English where possible. Evaluate the student's answer based on the rubric below.
Rubric:
{rubric_text}
Topic:
{topic}
Student Answer:
{student_answer}
Suggest ways for each aspect to improve, Be kind, supportive, and specific. Use at least 4 direct quotes from the essay where possible, and include improved versions.
"""
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            feedback = response.choices[0].message.content
        
        # Show feedback to student (outside the spinner)
        st.success("✅ Your answer has been submitted!")
        st.markdown("### 💬 Feedback")
        st.markdown(feedback)
        
        # Save to session and Google Sheet
        st.session_state.answers.append({
            "Name": name,
            "Topic": topic,
            "Answer": student_answer,
            "Feedback": feedback
        })
        
        # Add a spinner for the Google Sheets operation too
        with st.spinner('Saving your submission...'):
            sheet.append_row([name, topic, student_answer, feedback])
            
# === Teacher View (Hidden Table & Download) ===
# Divider
st.markdown("---")
st.subheader("👩‍🏫 Teacher Panel (Password Protected)")

# Password input (hidden text)
with st.expander("🔐 Enter Teacher Password"):
    pw_input = st.text_input("Password", type="password")
    
    if pw_input:
        try:
            teacher_pw = st.secrets["TEACHER_PASSWORD"]
            # Check if password matches
            if pw_input == teacher_pw:
                st.success("🔓 Access granted. Viewing teacher panel.")
                if st.session_state.answers:
                    df = pd.DataFrame(st.session_state.answers)
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download All Feedback", csv, "student_feedback.csv", "text/csv")
                else:
                    st.info("No submissions available yet.")
            else:
                st.error("❌ Incorrect password.")
        except KeyError:
            st.error("⚠️ TEACHER_PASSWORD is not configured in Streamlit secrets.")
