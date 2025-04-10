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
    word_count = len(student_answer.split())
max_words = 500  # Set your desired limit
# Display word count
st.caption(f"Word count: {word_count}/{max_words}")
# Check word limit during submission
if submitted:
    if word_count > max_words:
        st.error(f"Please limit your answer to {max_words} words. Current count: {word_count}")
    elif name and student_answer:
        # Process submission if within word limit
        # Your existing code here...    

if submitted and name and student_answer:
        
        # Generate feedback
        prompt = f"""
You are an assistant teacher helping a student improve their formal argumentative essay.. Evaluate the student's answer based on the rubric below.

Rubric:
{rubric_text}

Student Answer:
{student_answer}

Suggest ways to improve, Be kind, supportive, and specific. Use direct quotes from the essay where possible, and include improved versions.
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
    # Add a spinner for the Google Sheets operation too
    with st.spinner('Saving your submission...'):
        sheet.append_row([name, student_answer, feedback])
        # Save to Google Sheet
        sheet.append_row([name, student_answer, feedback])
# After successful submission
st.success("✅ Your answer has been submitted!")
st.balloons()  # Shows a cute balloon animation
st.markdown("### 💬 Feedback")
st.markdown(feedback)
# === Teacher View (Hidden Table & Download) ===
st.markdown("---")
st.subheader("👩‍🏫 Teacher Panel (Password Protected)")

# Always show the password input field
with st.expander("🔐 Enter Teacher Password"):
    pw_input = st.text_input("Password", type="password")
    
    if pw_input:
        # Try to get the password from secrets
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
