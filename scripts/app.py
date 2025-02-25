# app.py
import streamlit as st
import pdfplumber
import os
import sqlite3
import json
from h5p_builder import create_h5p_course_presentation

# Import API clients
from groq import Groq
from openai import OpenAI
import anthropic
from google.generativeai import configure as google_configure, GenerativeModel

# DB Functions
def init_db():
    conn = sqlite3.connect("prompt_frameworks.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS frameworks (id INTEGER PRIMARY KEY, name TEXT UNIQUE, prompt TEXT)''')
    examples = [
        ("Bloom's Taxonomy", "Generate questions aligned with Bloom's Taxonomy: 2 remembering, 2 understanding, 2 applying, 2 analyzing, 1 evaluating, 1 creating. Return in JSON format."),
        ("Socratic Method", "Generate questions that encourage critical thinking and exploration, following the Socratic Method. Return 10 questions in JSON format."),
        ("Simple Recall", "Generate straightforward recall questions to test basic comprehension of the text. Return 10 questions in JSON format.")
    ]
    c.executemany("INSERT OR IGNORE INTO frameworks (name, prompt) VALUES (?, ?)", examples)
    conn.commit()
    conn.close()

def get_frameworks():
    conn = sqlite3.connect("prompt_frameworks.db")
    c = conn.cursor()
    c.execute("SELECT name FROM frameworks")
    frameworks = [row[0] for row in c.fetchall()]
    conn.close()
    return frameworks

def get_prompt_by_name(name):
    conn = sqlite3.connect("prompt_frameworks.db")
    c = conn.cursor()
    c.execute("SELECT prompt FROM frameworks WHERE name = ?", (name,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def delete_framework(name):
    conn = sqlite3.connect("prompt_frameworks.db")
    c = conn.cursor()
    c.execute("DELETE FROM frameworks WHERE name = ?", (name,))
    conn.commit()
    conn.close()

init_db()

# API Client Setup
api_options = ["Groq", "OpenAI", "Claude", "Google Gemini"]
selected_api = st.sidebar.selectbox("Select API Provider", api_options)
api_key = st.sidebar.text_input(f"Enter {selected_api} API Key", type="password", key=f"{selected_api}_key")

def get_api_client(selected_api, api_key):
    if not api_key:
        st.error(f"Please enter an API key for {selected_api}.")
        return None
    if selected_api == "Groq":
        return Groq(api_key=api_key)
    elif selected_api == "OpenAI":
        return OpenAI(api_key=api_key)
    elif selected_api == "Claude":
        return anthropic.Anthropic(api_key=api_key)
    elif selected_api == "Google Gemini":
        google_configure(api_key=api_key)
        return GenerativeModel("gemini-1.5-flash")
    return None

def estimate_tokens(text):
    words = len(text.split())
    return int(words / 0.75)

def trim_text_to_token_limit(text, max_tokens=4000):
    words = text.split()
    token_count = estimate_tokens(" ".join(words))
    if token_count <= max_tokens:
        return text
    trimmed_words = words[:int(max_tokens * 0.75)]
    trimmed_text = " ".join(trimmed_words)
    return trimmed_text

def generate_questions_with_api(client, selected_api, pdf_text, content_type, leading_prompt):
    json_instruction = "Ensure the response is a valid JSON list of 10 objects, strictly formatted as requested, with no additional text."
    if content_type == "Multiple Choice":
        base_prompt = (
            f"{leading_prompt}\n\n{json_instruction}\n\nFrom the following text, generate 10 multiple-choice questions, each with 4 options and one correct answer. "
            f"Return the result as a JSON list of objects with 'question', 'options', and 'correct' keys.\n\nText:\n{pdf_text}"
        )
    elif content_type == "Fill in the Blanks":
        base_prompt = (
            f"{leading_prompt}\n\n{json_instruction}\n\nFrom the following text, generate 10 fill-in-the-blanks sentences, each with one blank and its answer. "
            f"Return the result as a JSON list of objects with 'text' and 'answer' keys.\n\nText:\n{pdf_text}"
        )
    elif content_type == "True/False":
        base_prompt = (
            f"{leading_prompt}\n\n{json_instruction}\n\nFrom the following text, generate 10 true/false statements, each with a question and a correct answer (True or False). "
            f"Return the result as a JSON list of objects with 'question' and 'correct' keys.\n\nText:\n{pdf_text}"
        )
    elif content_type == "Text":
        base_prompt = (
            f"{leading_prompt}\n\n{json_instruction}\n\nFrom the following text, generate 10 concise text snippets for presentation slides, each summarizing a key point. "
            f"Return the result as a JSON list of objects with 'text' keys.\n\nText:\n{pdf_text}"
        )

    if selected_api == "Groq":
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are an educational content creator. Follow the provided instructions precisely."},
                {"role": "user", "content": base_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    elif selected_api == "OpenAI":
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an educational content creator. Follow the provided instructions precisely."},
                {"role": "user", "content": base_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    elif selected_api == "Claude":
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.7,
            system="You are an educational content creator. Follow the provided instructions precisely.",
            messages=[{"role": "user", "content": base_prompt}]
        )
        return json.loads(response.content[0].text)
    elif selected_api == "Google Gemini":
        response = client.generate_content(base_prompt)
        return json.loads(response.text)
    return None

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# UI
st.title("H5P Material Generator")
st.write("Upload a PDF and generate a Course Presentation with 10 slides!")
frameworks = get_frameworks()
framework_option = st.sidebar.selectbox("Choose a framework (optional)", ["None", "Custom"] + frameworks, key="framework")
st.sidebar.subheader("Manage Frameworks")
framework_to_delete = st.sidebar.selectbox("Select framework to delete", frameworks if frameworks else ["None"], key="delete_framework")
delete_button = st.sidebar.button("Delete Framework")

pdf_file = st.file_uploader("Upload a PDF", type=["pdf"])
content_type = st.selectbox("Choose Activity Type for Slides", ["Multiple Choice", "Fill in the Blanks", "True/False", "Text"])
default_prompt = "Generate clear, concise questions based on the provided text."
prompt_input = st.text_area("Leading Prompt for LLM", value=default_prompt, height=100)
generate_button = st.button("Generate Course Presentation")

# Delete Logic
if delete_button and framework_to_delete and framework_to_delete != "None":
    delete_framework(framework_to_delete)
    st.sidebar.success(f"Deleted '{framework_to_delete}' successfully!")
    st.experimental_rerun()

# Generate Logic
if generate_button and pdf_file:
    client = get_api_client(selected_api, api_key)
    if client:
        pdf_text = extract_text_from_pdf(pdf_file)
        if not pdf_text:
            st.error("Failed to extract text from PDF.")
        else:
            trimmed_text = trim_text_to_token_limit(pdf_text, max_tokens=4000)
            if trimmed_text != pdf_text:
                st.warning("PDF text was trimmed to fit API token limits (approx. 4000 tokens). Some content may be excluded.")
            
            if framework_option == "Custom":
                leading_prompt = prompt_input
            elif framework_option == "None":
                leading_prompt = default_prompt
            else:
                leading_prompt = get_prompt_by_name(framework_option) or default_prompt

            st.write("Generating content with prompt:", leading_prompt)
            content = generate_questions_with_api(client, selected_api, trimmed_text, content_type, leading_prompt)
            if content:
                st.write("Generated Content (first 2 of 10):", content[:2])
                pdf_name = pdf_file.name.split(".")[0]
                h5p_file, md_file = create_h5p_course_presentation(pdf_name, content_type, content, f"{pdf_name}_{content_type}_Presentation.h5p")
                st.session_state["h5p_file"] = h5p_file  # Temporary storage in session state
                st.session_state["md_file"] = md_file    # Temporary storage in session state

# Display Download Buttons if Files Exist
if "h5p_file" in st.session_state and "md_file" in st.session_state:
    h5p_file = st.session_state["h5p_file"]
    md_file = st.session_state["md_file"]
    if os.path.exists(h5p_file) and os.path.exists(md_file):
        col1, col2 = st.columns(2)
        with col1:
            with open(h5p_file, "rb") as f:
                st.download_button("Download H5P Course Presentation", f, file_name=h5p_file, key="h5p_download")
        with col2:
            with open(md_file, "rb") as f:
                st.download_button("Download Questions Markdown", f, file_name=md_file, key="md_download")
    else:
        st.error("Generated files not found. Please regenerate.")
else:
    if generate_button:
        st.error("Failed to generate content from the selected API.")
