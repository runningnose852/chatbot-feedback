import streamlit as st
import openai
import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

if "answers" not in st.session_state:
    st.session_state.answers = []

if "results" not in st.session_state:
    st.session_state.results = []

st.set_page_config(page_title="📚 In-Class Chatbot with Rubric + CSV")

st.title("📚 In-Class Chatbot with Rubric-Based Feedback")

# Upload rubric file
uploaded_rubric = st.file_uploader("Upload rubric or model answer (.txt)", type="txt")

rubric_text = ""
if uploaded_rubric:
    rubric_text = uploaded_rubric.read().decode("utf-8")
    st.info("✅ Rubric/model answer loaded successfully.")

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
You are an assistant teacher evaluating student work. Use the following rubric to assess the student's answer.

Rubric:
{rubric_text}

Student's Answer:
{student_answer}

Based on the rubric, provide specific, constructive feedback:
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
