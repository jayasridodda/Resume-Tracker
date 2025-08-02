import streamlit as st
import pdfplumber
import re
import json
import spacy, subprocess

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Function to extract structured data from resume text
def extract_resume_data(resume_text):
    doc = nlp(resume_text)

    # Extract name (first PERSON entity)
    name_candidate = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name_candidate = ent.text
            break

    # Extract email
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", resume_text)
    email = email_match.group(0) if email_match else None

    # Extract skills
    skills_list = [
        "Python", "Java", "C++", "JavaScript", "SQL",
        "React.js", "Node.js", "Express.js", "MongoDB",
        "TensorFlow", "EfficientNet", "ResNet", "Random Forest", 
        "XGBoost", "Docker", "Firebase", "Figma"
    ]
    found_skills = [skill for skill in skills_list if skill.lower() in resume_text.lower()]

    # Extract degree
    degree_patterns = ["B\\.Tech", "M\\.Tech", "Bachelor", "Master"]
    degree = None
    for pattern in degree_patterns:
        match = re.search(pattern, resume_text, re.IGNORECASE)
        if match:
            degree = match.group()
            break

    # Extract institution
    institution_pattern = r"(College|University|Institute)[^\n]+"
    inst_match = re.search(institution_pattern, resume_text)
    institution = inst_match.group() if inst_match else None

    # Extract work experience lines
    experience_section = "\n".join(
        [line for line in resume_text.splitlines() if "intern" in line.lower() or "experience" in line.lower()]
    )

    return {
        "Name": name_candidate,
        "Email": email,
        "Skills": found_skills,
        "Degree": degree,
        "Institution": institution,
        "Work_Experience": experience_section.strip()
    }

# Streamlit UI
st.title("📄 Resume Parser with NLP")

uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        extracted_data = extract_resume_data(resume_text)

    st.subheader("Extracted Information:")
    st.json(extracted_data)
