import streamlit as st
from groq import Groq
import PyPDF2
import json
import time
from io import BytesIO

# PDF Libraries
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------
# CUSTOM CSS
# -----------------------------------

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.big-title {
    font-size: 48px;
    font-weight: bold;
    color: #4CAF50;
    text-align: center;
}

.sub-title {
    font-size: 20px;
    text-align: center;
    color: #BBBBBB;
}

.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    background-color: #4CAF50;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# HEADER
# -----------------------------------

st.markdown(
    '<p class="big-title">🤖 AI Resume Analyzer</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">Generative AI Powered ATS & Career Match System</p>',
    unsafe_allow_html=True
)

st.divider()

# -----------------------------------
# SIDEBAR
# -----------------------------------

st.sidebar.title("⚙ Settings")

api_key = st.secrets["GROQ_API_KEY"]

target_role = st.sidebar.selectbox(
    "Select Target Role",
    [
        "AI Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Analyst",
        "Generative AI Engineer"
    ]
)

# -----------------------------------
# PDF TEXT EXTRACTION
# -----------------------------------

def extract_text_from_pdf(uploaded_file):

    text = ""

    reader = PyPDF2.PdfReader(uploaded_file)

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# -----------------------------------
# PDF REPORT GENERATION
# -----------------------------------

def generate_pdf_report(result, target_role):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = []

    # TITLE
    title = Paragraph(
        "<font size=24><b>AI Resume Analysis Report</b></font>",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    # TARGET ROLE
    role = Paragraph(
        f"<font size=14><b>Target Role:</b> {target_role}</font>",
        styles['BodyText']
    )

    elements.append(role)
    elements.append(Spacer(1, 20))

    # ATS SCORE
    ats_heading = Paragraph(
        "<font size=18><b>ATS Compatibility Score</b></font>",
        styles['Heading2']
    )

    elements.append(ats_heading)

    ats = Paragraph(
        f"<font size=16 color='green'><b>{result['ats_score']}</b></font>",
        styles['BodyText']
    )

    elements.append(ats)
    elements.append(Spacer(1, 20))

    # STRENGTHS
    strengths_heading = Paragraph(
        "<font size=18><b>Strengths</b></font>",
        styles['Heading2']
    )

    elements.append(strengths_heading)

    for s in result["strengths"]:

        p = Paragraph(f"• {s}", styles['BodyText'])

        elements.append(p)

    elements.append(Spacer(1, 20))

    # WEAKNESSES
    weakness_heading = Paragraph(
        "<font size=18><b>Weaknesses</b></font>",
        styles['Heading2']
    )

    elements.append(weakness_heading)

    for w in result["weaknesses"]:

        p = Paragraph(f"• {w}", styles['BodyText'])

        elements.append(p)

    elements.append(Spacer(1, 20))

    # MISSING KEYWORDS
    keyword_heading = Paragraph(
        "<font size=18><b>Missing Keywords</b></font>",
        styles['Heading2']
    )

    elements.append(keyword_heading)
    elements.append(Spacer(1, 10))

    keyword_data = [[k] for k in result["missing_keywords"]]

    table = Table(keyword_data, colWidths=[450])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # SKILL GAP
    skill_heading = Paragraph(
        "<font size=18><b>Skill Gap Analysis</b></font>",
        styles['Heading2']
    )

    elements.append(skill_heading)

    skill_gap = Paragraph(
        result["skill_gap"],
        styles['BodyText']
    )

    elements.append(skill_gap)
    elements.append(Spacer(1, 20))

    # REWRITTEN SUMMARY
    summary_heading = Paragraph(
        "<font size=18><b>AI Rewritten Professional Summary</b></font>",
        styles['Heading2']
    )

    elements.append(summary_heading)

    summary = Paragraph(
        result["rewritten_summary"],
        styles['BodyText']
    )

    elements.append(summary)
    elements.append(Spacer(1, 20))

    # FINAL VERDICT
    verdict_heading = Paragraph(
        "<font size=18><b>Overall AI Verdict</b></font>",
        styles['Heading2']
    )

    elements.append(verdict_heading)

    verdict = Paragraph(
        result["overall_verdict"],
        styles['BodyText']
    )

    elements.append(verdict)

    # BUILD PDF
    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf

# -----------------------------------
# FILE UPLOADER
# -----------------------------------

uploaded_file = st.file_uploader(
    "📄 Upload Resume PDF",
    type=["pdf"]
)

# -----------------------------------
# ANALYZE BUTTON
# -----------------------------------

if uploaded_file and api_key:

    if st.button("🚀 Analyze Resume"):

        with st.spinner("Analyzing Resume with AI..."):

            progress = st.progress(0)

            for i in range(100):
                time.sleep(0.01)
                progress.progress(i + 1)

            # Extract Resume Text
            resume_text = extract_text_from_pdf(uploaded_file)

            # Initialize Groq Client
            client = Groq(api_key=api_key)

            # Prompt
            prompt = f"""
            You are an expert ATS Resume Analyzer and Career Coach.

            Analyze the following resume for the role: {target_role}

            Return ONLY valid JSON in this format:

            {{
              "ats_score": "85/100",
              "strengths": ["strength1", "strength2"],
              "weaknesses": ["weakness1", "weakness2"],
              "missing_keywords": ["keyword1", "keyword2"],
              "skill_gap": "summary",
              "rewritten_summary": "professional summary",
              "overall_verdict": "final verdict"
            }}

            RESUME:
            {resume_text}
            """

            # AI Response
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile"
            )

            result_text = response.choices[0].message.content

            cleaned = result_text.replace("```json", "").replace("```", "")

            result = json.loads(cleaned)

            # Generate PDF
            pdf_report = generate_pdf_report(
                result,
                target_role
            )

        st.success("✅ Analysis Completed Successfully")

        # -----------------------------------
        # ATS SCORE
        # -----------------------------------

        st.markdown("## 🎯 ATS Score")

        st.metric(
            label="ATS Compatibility",
            value=result["ats_score"]
        )

        # -----------------------------------
        # STRENGTHS
        # -----------------------------------

        st.markdown("## 💪 Strengths")

        for s in result["strengths"]:
            st.success(s)

        # -----------------------------------
        # WEAKNESSES
        # -----------------------------------

        st.markdown("## ⚠ Weaknesses")

        for w in result["weaknesses"]:
            st.warning(w)

        # -----------------------------------
        # MISSING KEYWORDS
        # -----------------------------------

        st.markdown("## 🔍 Missing Keywords")

        cols = st.columns(3)

        for i, keyword in enumerate(result["missing_keywords"]):
            cols[i % 3].info(keyword)

        # -----------------------------------
        # SKILL GAP
        # -----------------------------------

        st.markdown("## 📈 Skill Gap Analysis")

        st.info(result["skill_gap"])

        # -----------------------------------
        # REWRITTEN SUMMARY
        # -----------------------------------

        st.markdown("## ✨ AI Professional Summary")

        st.code(result["rewritten_summary"])

        # -----------------------------------
        # VERDICT
        # -----------------------------------

        st.markdown("## 🧠 Overall Verdict")

        st.success(result["overall_verdict"])

        # -----------------------------------
        # DOWNLOAD PDF
        # -----------------------------------

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_report,
            file_name="AI_Resume_Report.pdf",
            mime="application/pdf"
        )
