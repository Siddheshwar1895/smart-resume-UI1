import streamlit as st
import pdfplumber
import re
import uuid
import os
from fpdf import FPDF

st.set_page_config(page_title="Download Resume", layout="centered")
st.title("📄 Download Your ATS Ready Resume")

class ResumePDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, self.name, ln=True, align='L')
        self.set_font("Arial", '', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Email: {self.email} | Phone: +91-9876543210 | Location: India", ln=True)

    def section_title(self, title):
        self.set_font("Arial", 'B', 14)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def section_body(self, content, bullet=False):
        self.set_font("Arial", '', 12)
        self.set_text_color(60, 60, 60)
        if bullet:
            for line in content:
                self.cell(5)
                self.multi_cell(0, 8, f"- {line}")
        else:
            self.multi_cell(0, 8, content)
        self.ln(3)

    def build_resume(self, data):
        self.name = data['name']
        self.email = data['email']
        self.add_page()

        self.section_title("Profile Summary")
        self.section_body(data['summary'])

        self.section_title("Professional Summary")
        self.section_body(data['professional_summary'], bullet=True)

        self.section_title("Highest Education")
        self.section_body(data['education'])

        self.section_title("Experience")
        self.section_body(data['experience'], bullet=True)

        self.section_title("Projects")
        self.section_body(data['projects'], bullet=True)

        self.section_title("Job Responsibilities")
        self.section_body(data['responsibilities'], bullet=True)

        self.section_title("Personal Details")
        personal_details = [
            f"Full Name: {data['name']}",
            f"Email: {data['email']}",
            "Phone: +91-9876543210",
            "Location: India"
        ]
        self.section_body(personal_details, bullet=True)

def extract_text(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def clean(text):
    return re.sub(r"[^a-zA-Z0-9 ]", " ", text).lower()

def extract_keywords(text):
    return set(clean(text).split())

if "resume" in st.session_state and "jobtitle" in st.session_state:
    resume_text = extract_text(st.session_state.resume)
    jd_text = st.session_state.jobtitle
    resume_words = extract_keywords(resume_text)
    jd_words = extract_keywords(jd_text)
    missing = jd_words - resume_words

    resume_data = {
        "name": st.session_state.name,
        "email": st.session_state.email,
        "summary": "Proficient in " + ", ".join(list(missing)[:6]) + ".",
        "professional_summary": sorted(jd_words)[:6],
        "education": "B.Tech in Computer Science, XYZ University (2016)",
        "experience": ["QA Engineer at ABC Corp (2020-2023)", "Junior Tester at TechSoft (2018-2020)"],
        "projects": ["E-commerce Automation Suite", "Banking App Regression Testing"],
        "responsibilities": ["Design and execute test cases", "Bug tracking and documentation", "Collaboration with developers"]
    }

    pdf = ResumePDF()
    pdf.build_resume(resume_data)

    pdf_path = f"/tmp/ATS_Resume_{uuid.uuid4()}.pdf"
    pdf.output(pdf_path)

    with open(pdf_path, "rb") as f:
        st.markdown("""
        <style>
        body {
            background-color: white;
        }
        .stDownloadButton button {
            background-color: #f9d342;
            color: black;
            font-weight: bold;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)
st.download_button("📥 Download ATS Ready Resume (PDF)", f, file_name="ATS_Optimized_Resume.pdf")
else:
    st.warning("Please complete previous steps.")

st.markdown("[← Back to Home](../Home.py)", unsafe_allow_html=True)
