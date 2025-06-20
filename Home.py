import streamlit as st
import pdfplumber
import re
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

st.set_page_config(page_title='ATS Checker', layout='wide')

# Absolute background overlay
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-image: url('https://images.unsplash.com/photo-1605902711622-cfb43c4437d5?fit=crop&w=1500&q=80');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] { background: rgba(255,255,255,0.8); }
.block-container {
    background-color: rgba(255, 255, 255, 0.90);
    padding: 2rem;
    border-radius: 10px;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#2c3e50;'>📄 ATS Resume Checker</h1>", unsafe_allow_html=True)

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste Job Description or Job Title")
email = st.text_input("Enter Your Email")

match_clicked = st.button("Match")

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def clean(text):
    return re.sub(r"[^a-zA-Z0-9 ]", " ", text).lower()

def compute_score(resume_text, jd_text):
    documents = [resume_text, jd_text]
    vect = CountVectorizer().fit_transform(documents)
    return round(cosine_similarity(vect)[0][1] * 100, 2)

# Email restriction logic
email_file = Path("used_emails.json")
if not email_file.exists():
    email_file.write_text(json.dumps([]))
used_emails = json.loads(email_file.read_text())

if match_clicked:
    if email in used_emails:
        st.error("❌ This email has already used the ATS checker. Only one check allowed.")
    elif not resume_file or not job_description or not email:
        st.warning("⚠️ Please upload resume, paste JD, and enter email.")
    else:
        resume_text = clean(extract_text_from_pdf(resume_file))
        jd_text = clean(job_description)
        score = compute_score(resume_text, jd_text)

        st.markdown(f"""<h2 style='color:green;'>✅ ATS Match Score: <span style='font-size:28px;'>{score}%</span></h2>""", unsafe_allow_html=True)

        resume_words = set(resume_text.split())
        jd_words = set(jd_text.split())
        matched = resume_words & jd_words
        missing = jd_words - resume_words

        st.subheader("✅ Matched Keywords")
        st.write(", ".join(list(matched)[:50]))
        st.subheader("❌ Missing Keywords")
        st.write(", ".join(list(missing)[:20]))

        st.markdown("---")
        st.info("Want to improve your ATS score to 100%?")
        st.page_link("pages/1_UpgradeResume.py", label="Upgrade My Resume", icon="🔁")

        # Save used email
        used_emails.append(email)
        email_file.write_text(json.dumps(used_emails))
