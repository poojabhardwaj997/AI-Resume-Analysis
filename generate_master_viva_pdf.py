import os
import sys
import html
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))

            # Running Header
            self.drawString(36, 758, "BSc IT FINAL YEAR EXTERNAL VIVA MASTER GUIDE — TALENTLENS AI")
            self.setFont("Helvetica", 8)
            self.drawRightString(576, 758, "poojabhardwaj997/AI-Resume-Analysis")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 752, 576, 752)

            # Running Footer
            self.line(36, 44, 576, 44)
            self.setFont("Helvetica", 7.5)
            self.drawString(36, 32, "Confidential Academic Manual — Complete Architecture, ML Models, Workflow & 65+ Viva Q&A")
            self.drawRightString(576, 32, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()


def callout(title: str, text: str, border_color: str, bg_color: str, styles):
    title_style = ParagraphStyle(
        'CalloutTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor(border_color),
        spaceAfter=2,
    )
    body_style = ParagraphStyle(
        'CalloutBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=colors.HexColor('#1e293b'),
    )
    content = [
        Paragraph(f"<b>{title}</b>", title_style),
        Paragraph(text, body_style)
    ]
    t = Table([[content]], colWidths=[540])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def build_master_viva_manual(output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=base_styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=base_styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e1b4b'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=base_styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#312e81'),
        spaceBefore=7,
        spaceAfter=2,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=colors.HexColor('#1e293b'),
        alignment=TA_JUSTIFY,
        spaceAfter=3,
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2,
    )
    qa_q = ParagraphStyle(
        'QAQ',
        parent=base_styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=11,
        textColor=colors.HexColor('#1e1b4b'),
        spaceBefore=4,
        spaceAfter=1,
        keepWithNext=True,
    )
    qa_a = ParagraphStyle(
        'QAA',
        parent=base_styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=8,
        spaceAfter=3,
    )

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 10))
    badge = ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.HexColor('#4338ca'), alignment=TA_CENTER)
    story.append(Paragraph("★ BSc IT FINAL YEAR PROJECT — COMPREHENSIVE EXTERNAL VIVA MASTER HANDBOOK ★", badge))
    story.append(Spacer(1, 8))

    story.append(Paragraph("AI-Powered Resume Analysis API with Skill Gap Detection using LLMs", title_style))
    story.append(Paragraph(
        "Complete Project Explanation in Simple Hinglish: System Architecture, AI/LLM Models, Workflow, Database Schema, Mathematics, and 65+ External Viva Questions & Answers",
        sub_style
    ))

    # Meta Table
    meta_rows = [
        [Paragraph("<b>Project Title:</b>", body_style), Paragraph("AI-Powered Resume Analysis API with Skill Gap Detection using LLMs (TalentLens AI)", body_style)],
        [Paragraph("<b>Candidate Name & Course:</b>", body_style), Paragraph("Pooja Bhardwaj | B.Sc. in Information Technology (BSc IT Final Year)", body_style)],
        [Paragraph("<b>Live Website (Vercel):</b>", body_style), Paragraph("https://ai-resume-analysis-frontend-orcin.vercel.app/", body_style)],
        [Paragraph("<b>Live Backend API (Render):</b>", body_style), Paragraph("https://ai-resume-backend-61zn.onrender.com (Swagger Docs: /docs)", body_style)],
        [Paragraph("<b>GitHub Repository:</b>", body_style), Paragraph("https://github.com/poojabhardwaj997/AI-Resume-Analysis.git (Branch: main)", body_style)],
        [Paragraph("<b>Database & Storage:</b>", body_style), Paragraph("Supabase Managed PostgreSQL (8 Tables + Profiles + Audit Logs + RLS)", body_style)],
        [Paragraph("<b>Primary AI Model:</b>", body_style), Paragraph("OpenAI GPT-4o-mini (JSON Schema Mode) + Intelligent Python Heuristic Fallback", body_style)],
        [Paragraph("<b>Testing & Verification:</b>", body_style), Paragraph("55 / 55 Passed Unit & Integration Tests (100% Pass Rate via pytest)", body_style)],
        [Paragraph("<b>Document Purpose:</b>", body_style), Paragraph("External Viva Defense, Examiner Questions Preparation & In-Depth Technical Revision", body_style)],
    ]
    meta_t = Table(meta_rows, colWidths=[140, 400])
    meta_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 10))

    exec_box = (
        "<b>Examiner ko impress karne ke liye essential guidance:</b><br/>"
        "Yeh manual un sabhi technical sawalon ka answer deta hai jo external examiner viva mein poochte hain: "
        "<i>'Kaunsa ML model use hua?', 'Kyun use hua?', 'Scoring ka mathematical formula kya hai?', 'Transferable skill kya hoti hai?', "
        "'Database me kaunse tables hain?', 'Agar AI API down ho jaye toh kya hoga?'</i>. "
        "Har topic simple Hinglish mein explained hai taaki aap ratta marne ke bajaye naturally explain kar sakein."
    )
    story.append(callout("VIVA PREPARATION ROADMAP", exec_box, "#4f46e5", "#eef2ff", base_styles))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: PROJECT OVERVIEW
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: Project Overview & Core Mission", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    story.append(Paragraph("1.1 Project ka Asli Introduction", h2_style))
    story.append(Paragraph(
        "Mera project ek modern, AI-assisted recruitment analysis platform aur RESTful API service hai jiska naam <b>TalentLens AI</b> hai. "
        "Yeh job seekers aur recruiters ke beech ke communication gap ko bridge karta hai. "
        "Jab koi user apna resume (PDF ya Word document) upload karta hai aur target Job Description (JD) enter karta hai, "
        "toh hamara system dono documents ko analyze karke missing skills detect karta hai, candidate ke background ko compare karta hai, "
        "aur transparent score ke sath unhe personalized career upskilling roadmaps deta hai.",
        body_style
    ))

    story.append(Paragraph("1.2 Ye Project Kaunsi Problem Solve Karta Hai?", h2_style))
    story.append(Paragraph(
        "Pura recruitment ecosystem 2 badi problems se suffer kar raha tha:<br/>"
        "1. <b>Manual Screening ki Slow Speed:</b> HR recruiters ko hazaron resumes haath se dekhne padte hain, jisme human fatigue aur unconscious bias aana common hai.<br/>"
        "2. <b>Legacy ATS (Applicant Tracking System) ka Rigid Keyword Matching:</b> Purane systems sirf exact text match karte hain. Agar job me 'React' maanga hai aur candidate ne 'React.js' ya 'Next.js' likha hai, toh traditional ATS candidate ko reject kar deta hai bina koi wajah bataye.<br/>"
        "3. <b>Zero Candidate Feedback:</b> 99% candidates ko sirf 'Application Rejected' ka cold email milta hai. Unhe yeh nahi pata chalta ki unme kaunsi specific skill missing thi aur use kahan se seekha ja sakta hai.<br/>"
        "<b>Hamara Solution:</b> TalentLens AI rejection ke badle <i>Skill Gap Intelligence</i> aur <i>Actionable Learning Roadmaps</i> provide karta hai.",
        body_style
    ))

    story.append(Paragraph("1.3 Multi-Degree Support (B.Com, BBA, BCA, BSc IT, AI, Data Science)", h2_style))
    story.append(Paragraph(
        "<b>Viva Point:</b> Examiner pooch sakta hai: <i>'Kya yeh sirf Software Developers ke liye hai?'</i><br/>"
        "<b>Answer:</b> Bilkul nahi Sir! Humne backend mein ek <b>Cross-Domain Skill Normalizer</b> banaya hai jisme 300+ skills categorized hain:<br/>"
        "• <b>IT / CS / BCA / BSc IT:</b> Python, FastAPI, Java, React, SQL, Docker, Kubernetes, AWS, Git, REST APIs.<br/>"
        "• <b>Data Science & AI:</b> Machine Learning, Deep Learning, Pandas, NumPy, Scikit-Learn, Power BI, Tableau, NLP.<br/>"
        "• <b>Finance & B.Com:</b> Accounting, Tally ERP, Financial Modeling, Auditing, Taxation, GST, Advanced Excel.<br/>"
        "• <b>HR & BBA:</b> Talent Acquisition, Payroll Management, Agile/Scrum, Employee Engagement, Communication Skills.",
        body_style
    ))

    pitches = (
        "<b>30-Second Viva Pitch (Examiner ke samne pehle 30 seconds me ye bolna):</b><br/>"
        "<i>'Respected Examiner, mera project TalentLens AI ek AI-Powered Resume Analysis platform hai. Yeh uploaded PDF/DOCX resume aur Job Description ko LLM aur NLP techniques ke zariye parse karta hai, canonical skill taxonomy se normalize karta hai, aur transferable skills ko recognize karke ek transparent weighted compatibility score aur actionable learning roadmap provide karta hai. Iska backend FastAPI aur frontend React 18 par built hai, aur database Supabase PostgreSQL use karta hai.'</i><br/><br/>"
        "<b>1-Minute Technical Pitch:</b><br/>"
        "<i>'Sir, traditional ATS keyword matching par based hote hain jo minor spelling ya synonym difference par candidate ko disqualify kar dete hain. Mere project mein hum OpenAI GPT-4o-mini structured JSON mode aur PyMuPDF parsing use karte hain resume entities extract karne ke liye. Phir Python-based deterministic logic se skills ko normalize kiya jata hai. Hum 4 categories mein skills ko divide karte hain: Matched (with textual evidence), Missing Required, Transferable (credited with 0.5 weight), aur Preferred gaps. Iske baad ek 4-pillar weighted formula se 0-100% compatibility score calculate hota hai, aur missing skills ke liye automated courses aur projects recommend hote hain. System Supabase PostgreSQL aur JWT authentication se fully secured hai aur 55 passing automated tests se verified hai.'</i>"
    )
    story.append(callout("ELEVATOR PITCHES FOR VIVA", pitches, "#10b981", "#ecfdf5", base_styles))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: TECHNOLOGY STACK
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: Verified Technology Stack & Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    tech_rows = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Actual Technology</b>", body_style), Paragraph("<b>Kyun Use Ki (Why Chosen)</b>", body_style), Paragraph("<b>Implementation Status</b>", body_style)],
        [Paragraph("Frontend UI", body_style), Paragraph("React 18 + Vite", body_style), Paragraph("Fast compilation (ESBuild/Rollup), Component architecture, SPA routing.", body_style), Paragraph("Verified (Vercel Live)", body_style)],
        [Paragraph("Styling System", body_style), Paragraph("Vanilla CSS (index.css)", body_style), Paragraph("Full control on CSS custom properties (variables), dark-mode glassmorphism.", body_style), Paragraph("Verified", body_style)],
        [Paragraph("Backend API", body_style), Paragraph("Python 3.13 + FastAPI", body_style), Paragraph("Asynchronous execution (ASGI), Pydantic v2 data validation, automated Swagger.", body_style), Paragraph("Verified (Render Live)", body_style)],
        [Paragraph("PDF Text Extractor", body_style), Paragraph("PyMuPDF (fitz 1.28.2)", body_style), Paragraph("C-accelerated MuPDF bindings; multi-column resume layouts ko accurately padhta hai.", body_style), Paragraph("Verified", body_style)],
        [Paragraph("Word Doc Extractor", body_style), Paragraph("python-docx (1.2.0)", body_style), Paragraph("Word XML parse karke standard paragraphs aur multi-column tables nikalta hai.", body_style), Paragraph("Verified", body_style)],
        [Paragraph("AI / LLM Model", body_style), Paragraph("OpenAI GPT-4o-mini", body_style), Paragraph("JSON schema mode support, zero-hallucination prompt, fast response (1-2s), cost-effective.", body_style), Paragraph("Verified + Heuristic Fallback", body_style)],
        [Paragraph("Cloud Database", body_style), Paragraph("Supabase PostgreSQL", body_style), Paragraph("ACID relational database, JSONB columns, performance B-tree indexes.", body_style), Paragraph("Verified", body_style)],
        [Paragraph("Authentication", body_style), Paragraph("Supabase Auth (JWT)", body_style), Paragraph("Secure bearer tokens, encrypted password hashing, Row Level Security (RLS).", body_style), Paragraph("Verified", body_style)],
        [Paragraph("Testing Suite", body_style), Paragraph("pytest + pytest-asyncio", body_style), Paragraph("55 unit & integration tests covering security, parsing, and scoring logic.", body_style), Paragraph("Verified (55/55 Passed)", body_style)],
        [Paragraph("Deployment Hosts", body_style), Paragraph("Vercel (UI) + Render (API)", body_style), Paragraph("Vercel Edge CDN for SPA; Render containerized Python 3.13 service.", body_style), Paragraph("Verified Live", body_style)],
    ]
    tech_table = Table(tech_rows, colWidths=[85, 110, 245, 100])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 8))

    diff_box = (
        "<b>Critical Viva Distinction (Examiner Question: 'Frontend vs Backend vs Database vs API vs AI/LLM'):</b><br/>"
        "• <b>Frontend (React 18):</b> Client-side layer jo user ke browser par render hota hai. Forms, buttons, score gauge aur CSS styles yahan handle hote hain.<br/>"
        "• <b>Backend (FastAPI):</b> Server-side business logic jo cloud server par chalta hai. File bytes validation, authentication check, scoring calculation aur database queries yahan run hoti hain.<br/>"
        "• <b>Database (Supabase PostgreSQL):</b> Permanent storage jahan users, resumes, analyses aur audit logs tables me store hote hain.<br/>"
        "• <b>API (Application Programming Interface):</b> Frontend aur Backend ke beech ka communication bridge jo standard HTTP protocols aur JSON format me data transfer karta hai.<br/>"
        "• <b>AI / LLM (OpenAI GPT-4o-mini):</b> Natural language understanding layer jo unstructured resume English text ko structured JSON object me convert karta hai."
    )
    story.append(callout("ARCHITECTURE ROLES EXPLAINED", diff_box, "#6366f1", "#f8fafc", base_styles))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: MACHINE LEARNING & AI/LLM MODELS
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: Machine Learning & AI/LLM Models (VIVA SPECIAL)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    ai_warn = (
        "<b>EXAMINER KA FAVORITE QUESTION: 'Kya tumne apna Machine Learning model scratch se train kiya?'</b><br/>"
        "<b>Direct & Honest Answer:</b><br/>"
        "<i>'No Sir. Ek Large Language Model ko scratch se train karne ke liye hazaron GPUs aur millions of parameters ka budget chahiye hota hai. "
        "Production grade software engineering mein best practice yeh hoti hai ki hum pre-trained foundation models ko use karein. "
        "Humne OpenAI ka <b>gpt-4o-mini</b> model use kiya hai via official API with strict <b>JSON Schema Mode</b> aur System Prompting. "
        "Humne model ko hallucination se rokne ke liye strict extraction boundaries di hain, aur mathematical scoring humne code mein deterministic formula se calculate ki hai.'</i>"
    )
    story.append(callout("HONEST TECHNICAL ANSWER", ai_warn, "#dc2626", "#fef2f2", base_styles))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.1 Kyun Traditional ML ke badle LLM use kiya?", h2_style))
    story.append(Paragraph(
        "Examiner pooch sakta hai: <i>'Scikit-learn, TF-IDF ya spaCy kyun nahi use kiya?'</i><br/>"
        "1. <b>Contextual Understanding:</b> TF-IDF ya Naive Bayes sirf word frequency count karte hain. Woh yeh nahi samajh sakte ki 'Worked on Python for 2 years' ek full-time experience hai jabki 'Created a simple Python script in college' ek hobby project hai.<br/>"
        "2. <b>Zero-Shot Extraction:</b> LLM bina kisi custom dataset ke complex English sentences ko padh kar candidate ka name, email, phone, company, role, education aur skills extract kar leta hai.<br/>"
        "3. <b>Multi-Domain Flexibility:</b> Traditional ML models ko har domain (IT, Finance, HR) ke liye alag se train karna padta hai, jabki LLM multi-domain text ko effortlessly comprehend karta hai.",
        body_style
    ))

    story.append(Paragraph("3.2 OpenAI GPT-4o-mini ka Exact Workflow & Prompts", h2_style))
    story.append(Paragraph(
        "Backend file <code>app/services/llm_service.py</code> mein 2 structured system prompts hain:<br/>"
        "• <b>Resume Extraction Prompt:</b> Model ko instruct kiya jata hai: <i>'You are an expert HR Data Scientist. Parse unstructured resume text into strict JSON matching CandidateProfile schema. RULE: NEVER hallucinate or invent qualifications not explicitly stated. If not found, return null or empty list.'</i><br/>"
        "• <b>Job Description Prompt:</b> Model ko instruct kiya jata hai: <i>'Distinguish between REQUIRED skills (mandatory) and PREFERRED skills (nice-to-have, bonus).'</i>",
        body_style
    ))

    story.append(Paragraph("3.3 Intelligent Heuristic Fallback System (Zero Crash Guarantee)", h2_style))
    story.append(Paragraph(
        "Examiner pooch sakta hai: <i>'Agar OpenAI ka internet band ho jaye ya API quota khatam ho jaye, toh tumhara system fail ho jayega?'</i><br/>"
        "<b>Answer:</b> <b>Bilkul nahi Sir!</b> Hamare code (<code>llm_service.py</code> line 98-103) mein ek intelligent <b>Regex Heuristic Fallback Parser</b> likha hua hai.<br/>"
        "Agar OpenAI API call fail hoti hai (jaise HTTP 429 quota exhausted), system automatically exception catch karta hai aur local Python regex pattern matching engine chala deta hai. "
        "Woh email, phone number, education degrees, aur 300+ skills ko bina kisi external API call ke local CPU par extract kar leta hai. Isse application 100% reliable rehti hai.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: SKILL GAP DETECTION & MATHEMATICAL SCORING
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: Skill Gap Detection & Scoring Mathematics", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    story.append(Paragraph("4.1 Skill Comparison Algorithm", h2_style))
    story.append(Paragraph(
        "Backend file <code>app/services/skill_gap.py</code> yeh core matching perform karti hai:<br/>"
        "1. <b>Canonical Normalization:</b> <code>skill_normalizer.py</code> raw skills ko clean karta hai (punctuation hatana, lowercase karna) aur synonyms map karta hai (e.g., `JS` $\rightarrow$ `JavaScript`).<br/>"
        "2. <b>Direct Matches:</b> Agar canonical skill candidate aur JD dono me hai $\rightarrow$ <b>Matched (1.0 weight)</b>. Saath hi resume raw text me regex scan karke woh exact sentence dhundh kar evidence quote attach kiya jata hai.<br/>"
        "3. <b>Transferable Skills (Partial Credit):</b> Agar required skill candidate ke paas nahi hai, toh system <code>RELATED_SKILL_CLUSTERS</code> check karta hai. "
        "Agar candidate ke paas sibling skill hai (e.g. FastAPI missing, but Django present) $\rightarrow$ <b>Transferable (0.5 weight)</b> diya jata hai.<br/>"
        "4. <b>Missing Required Skills:</b> Jo skills bilkul present nahi hain $\rightarrow$ <b>Missing (0.0 weight)</b>, aur inhi ke liye automated learning roadmaps generate hote hain.<br/>"
        "5. <b>Preferred Skills:</b> Nice-to-have bonus competencies ko separately track kiya jata hai.",
        body_style
    ))

    formula_box = (
        "<b>SCORING FORMULA (Examiner ko board/paper par ye likh kar dikhana):</b><br/>"
        "<code>Overall Compatibility Score = (RequiredScore × 0.60) + (PreferredScore × 0.15) + (ExperienceScore × 0.15) + (EducationScore × 0.10)</code><br/><br/>"
        "<b>Step-by-Step Mathematical Example:</b><br/>"
        "• <b>Job Requirements:</b> 4 Required Skills (`Python`, `FastAPI`, `Docker`, `PostgreSQL`), 2 Preferred (`Kubernetes`, `Redis`), 2 Years Experience, Bachelor degree.<br/>"
        "• <b>Candidate Resume:</b> `Python`, `Django`, `PostgreSQL`, 2 Years Experience, BSc IT.<br/><br/>"
        "1. <b>RequiredScore ($S_{\\text{req}}$):</b> Direct Matches = 2 (`Python`, `PostgreSQL`). Transferable = 1 (`FastAPI` via `Django`).<br/>"
        "   Effective Matches = $2 + (1 \\times 0.5) = 2.5$.<br/>"
        "   $S_{\\text{req}} = \\frac{2.5}{4} \\times 100 = \\mathbf{62.5\\%}$. Contribution to Total = $62.5 \\times 0.60 = \\mathbf{37.5}$.<br/>"
        "2. <b>PreferredScore ($S_{\\text{pref}}$):</b> Candidate has 0 preferred skills.<br/>"
        "   $S_{\\text{pref}} = \\frac{0}{2} \\times 100 = 0\\%$. Contribution to Total = $0 \\times 0.15 = \\mathbf{0}$.<br/>"
        "3. <b>ExperienceScore ($S_{\\text{exp}}$):</b> Candidate has 2 years, Job required 2 years.<br/>"
        "   $S_{\\text{exp}} = \\min(\\frac{2}{2}, 1.0) \\times 100 = 100\\%$. Contribution to Total = $100 \\times 0.15 = \\mathbf{15.0}$.<br/>"
        "4. <b>EducationScore ($S_{\\text{edu}}$):</b> Candidate has relevant degree (`BSc IT`).<br/>"
        "   $S_{\\text{edu}} = 100\\%$. Contribution to Total = $100 \\times 0.10 = \\mathbf{10.0}$.<br/><br/>"
        "<b>Final Total Score:</b> $37.5 + 0.0 + 15.0 + 10.0 = \\mathbf{62.50\\%}$."
    )
    story.append(callout("EXACT MATHEMATICAL ENGINE", formula_box, "#10b981", "#ecfdf5", base_styles))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: DATABASE ARCHITECTURE (SUPABASE)
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: Database Architecture & Supabase PostgreSQL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    story.append(Paragraph("5.1 Supabase ka Role aur Setup", h2_style))
    story.append(Paragraph(
        "Humne **Supabase Managed PostgreSQL** use kiya hai. "
        "Supabase hume 3 major capabilities provide karta hai:<br/>"
        "1. <b>PostgreSQL Relational DB:</b> ACID-compliant tables, foreign keys aur JSONB semi-structured storage.<br/>"
        "2. <b>Supabase Auth:</b> Built-in user management with encrypted passwords aur JWT bearer token issuance.<br/>"
        "3. <b>Row Level Security (RLS):</b> Har user ka data isolate karne ke liye database-level policies.",
        body_style
    ))

    db_rows = [
        [Paragraph("<b>Table Name</b>", body_style), Paragraph("<b>Purpose</b>", body_style), Paragraph("<b>Important Columns</b>", body_style), Paragraph("<b>Primary Key</b>", body_style), Paragraph("<b>Foreign Key & Cascade</b>", body_style)],
        [Paragraph("`profiles`", body_style), Paragraph("User account profile identity", body_style), Paragraph("`id`, `full_name`, `email`, `created_at`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`auth.users(id)` ON DELETE CASCADE", body_style)],
        [Paragraph("`resumes`", body_style), Paragraph("Uploaded resume metadata & text", body_style), Paragraph("`file_name`, `file_type`, `raw_text`, `parsed_profile (JSONB)`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`user_id -> profiles(id)`", body_style)],
        [Paragraph("`job_descriptions`", body_style), Paragraph("Target job post criteria", body_style), Paragraph("`job_title`, `company_name`, `raw_text`, `parsed_requirements (JSONB)`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`user_id -> profiles(id)`", body_style)],
        [Paragraph("`candidate_skills`", body_style), Paragraph("Normalized candidate competencies", body_style), Paragraph("`skill_name`, `normalized_name`, `category`, `proficiency`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`resume_id -> resumes(id)` ON DELETE CASCADE", body_style)],
        [Paragraph("`job_skills`", body_style), Paragraph("Normalized target job criteria", body_style), Paragraph("`skill_name`, `normalized_name`, `requirement_type`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`job_id -> job_descriptions(id)` ON DELETE CASCADE", body_style)],
        [Paragraph("`analyses`", body_style), Paragraph("Master compatibility report", body_style), Paragraph("`compatibility_score`, `required_score`, `preferred_score`, `experience_score`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`resume_id`, `job_id`, `user_id`", body_style)],
        [Paragraph("`skill_gaps`", body_style), Paragraph("Individual skill status & proof", body_style), Paragraph("`skill_name`, `status`, `evidence`, `explanation`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`analysis_id -> analyses(id)` ON DELETE CASCADE", body_style)],
        [Paragraph("`recommendations`", body_style), Paragraph("Personalized upskilling roadmaps", body_style), Paragraph("`skill_name`, `learning_objective`, `practical_exercise`, `suggested_project`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`analysis_id -> analyses(id)` ON DELETE CASCADE", body_style)],
        [Paragraph("`audit_logs`", body_style), Paragraph("Security compliance tracking", body_style), Paragraph("`action`, `resource_type`, `resource_id`, `ip_address`, `created_at`", body_style), Paragraph("`id (UUID)`", body_style), Paragraph("`user_id -> profiles(id)`", body_style)],
    ]
    db_t = Table(db_rows, colWidths=[75, 110, 160, 75, 120])
    db_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(db_t)
    story.append(Spacer(1, 8))

    rls_box = (
        "<b>Row Level Security (RLS) Explanation:</b><br/>"
        "PostgreSQL mein RLS enable karke hum ensure karte hain ki user sirf apna data dekh ya delete kar sake. "
        "Backend FastAPI server `SUPABASE_SERVICE_ROLE_KEY` ke zariye authenticate karta hai jisse woh securely transactional operations perform kar sake, "
        "jabki har request ke user JWT token se verify hoti hai ki User A kabhi User B ka resume access na kare (IDOR Protection)."
    )
    story.append(callout("DATABASE SECURITY & RLS", rls_box, "#6366f1", "#f8fafc", base_styles))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: END-TO-END WORKFLOW & DIAGRAMS
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: End-to-End System Workflow & Diagrams", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    story.append(Paragraph("6.1 Detailed 8-Stage Processing Lifecycle", h2_style))
    stages = [
        "<b>Stage 1: User Uploads Documents:</b> Candidate resume file (.pdf ya .docx) choose karta hai aur Target Job Description paste karta hai (ya 1-click sample button press karta hai).",
        "<b>Stage 2: Validation Layer:</b> Backend file extension, MIME type, file size (< 10MB) aur magic bytes check karta hai. Scanned PDF hone par (< 40 characters) HTTP 422 error throw karta hai.",
        "<b>Stage 3: Text Extraction:</b> PyMuPDF (`fitz`) vector PDF se text nikalta hai; python-docx Word paragraphs aur tables se content extract karta hai.",
        "<b>Stage 4: Entity Extraction (LLM / Heuristic):</b> OpenAI `gpt-4o-mini` structured JSON mode me resume aur JD ko parse karta hai. Quota khatam hone par Heuristic Regex fallback chalta hai.",
        "<b>Stage 5: Canonical Normalization:</b> 300+ skills dictionary aliases ko standard names me convert karti hai.",
        "<b>Stage 6: Skill Gap & Transferable Evaluation:</b> Skills ko 4 categories me segregate kiya jata hai: Matched, Missing Required, Transferable (0.5 credit), aur Preferred gaps.",
        "<b>Stage 7: Weighted Scoring:</b> Deterministic Python formula 0-100% compatibility score aur 4 sub-scores calculate karta hai.",
        "<b>Stage 8: Upskilling Synthesis & DB Storage:</b> Missing skills ke courses attach hote hain, Supabase PostgreSQL me records save hote hain, aur React Dashboard par animated report display hoti hai.",
    ]
    for s in stages:
        story.append(Paragraph(f"• {s}", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("6.2 Data Flow Architecture Diagram (ASCII):", h2_style))
    diag_text = """
 [ Browser Client (React 18) ]  
        │  1. Multipart Form (Resume File + Job Description Text)
        ▼
 [ FastAPI Server (Python 3.13) ]
        │  2. File Validation & PyMuPDF / python-docx Extraction
        ▼
 [ Extracted Clean Raw Text ]
        │  3. Structured Extraction Prompt (JSON Schema Mode)
        ▼
 [ OpenAI GPT-4o-mini API ]  ──(If Offline/Quota Full)──>  [ Local Regex Heuristic Parser ]
        │  4. Structured CandidateProfile & JobRequirements JSON
        ▼
 [ Canonical Skill Normalizer ]
        │  5. Maps Synonyms & Identifies Transferable Competencies (0.5x credit)
        ▼
 [ Deterministic Scoring Engine ]
        │  6. Computes 60% Required + 15% Preferred + 15% Exp + 10% Edu
        ▼
 [ Actionable Recommendation Engine ]
        │  7. Synthesizes Tailored Course Roadmaps & Beginner Drills
        ▼
 [ Supabase PostgreSQL Storage ]  <──  8. Persists to 8 Tables with RLS & Audit Logs
        │  9. Returns JSON Response
        ▼
 [ Visual Results Dashboard (React 18) ]  ──>  [ 1-Click Printable PDF Export ]
    """
    diag_p = ParagraphStyle('DiagP', fontName='Courier', fontSize=6.5, leading=8.5, textColor=colors.HexColor('#0f172a'))
    story.append(Table([[Paragraph(html.escape(diag_text).replace(" ", "&nbsp;").replace("\n", "<br/>"), diag_p)]], colWidths=[540]))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7: 50 EXTERNAL VIVA QUESTIONS & HINGLISH ANSWERS
    # =========================================================================
    story.append(Paragraph("CHAPTER 7: Top 50 External Viva Questions & Answers", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    viva_qas = [
        ("1. What is the title of your project?", "Sir, mera project title hai 'AI-Powered Resume Analysis API with Skill Gap Detection using LLMs'."),
        ("2. Project ka main objective kya hai?", "Resume aur Job Description ko compare karke missing skills identify karna, transferable skills ko recognition dena, transparent score nikalna aur personalized learning roadmap dena."),
        ("3. Traditional ATS se tumhara system kaise better hai?", "Traditional ATS rigid keyword search karte hain aur candidate ko reject kar dete hain. Hum synonyms normalize karte hain, transferable skills ko partial credit dete hain aur candidate ko upskilling guidance dete hain."),
        ("4. Which frontend framework did you choose and why?", "React 18 with Vite. Vite ultra-fast build tool hai aur React reusable component architecture aur SPA routing provide karta hai."),
        ("5. Which backend framework is used?", "Python 3.13 with FastAPI. FastAPI asynchronous I/O support karta hai, high performance hai aur Pydantic v2 data validation provide karta hai."),
        ("6. What is ASGI and why does FastAPI use it?", "ASGI means Asynchronous Server Gateway Interface. Yeh multiple concurrent requests ko bina blocking handle karta hai using Python asyncio."),
        ("7. Which AI/LLM model is running in your project?", "OpenAI ka pre-trained foundation model 'gpt-4o-mini' use ho raha hai through official API with strict JSON schema mode."),
        ("8. Did you train this AI model yourself?", "No Sir. Foundation models ko scratch se train karna enterprise infrastructure require karta hai. Humne pre-trained model ko Prompt Engineering aur Structured Output schema ke through guide kiya hai."),
        ("9. Why use an LLM instead of traditional Machine Learning?", "Traditional ML (jaise TF-IDF ya Naive Bayes) context nahi samajhte. LLM unstructured resume sentences se accurate context extract kar leta hai."),
        ("10. What happens if the OpenAI API fails or quota runs out?", "System crash nahi hota. Humne backend mein intelligent Regex Heuristic Fallback parser banaya hai jo local Python engine par chalta hai."),
        ("11. How do you extract text from PDF files?", "PyMuPDF (`fitz`) library ke through, jo C-level bindings use karti hai aur multi-column resume layouts ko accurately extract karti hai."),
        ("12. How do you handle scanned image PDFs?", "Extracted characters count check karte hain. Agar text 40 characters se kam ho, toh system HTTP 422 error throw karke digital PDF upload karne ko bolta hai."),
        ("13. How do you extract text from Word (.docx) files?", "python-docx library use ki hai jo standard paragraphs aur 2-column tables dono se text extract karti hai."),
        ("14. What is a Transferable Skill in your system?", "Jab candidate ke paas required skill nahi hoti lekin uski adjacent/sibling skill hoti hai (e.g. FastAPI ke badle Django/Flask), toh system use partial credit (0.5 weight) deta hai."),
        ("15. How is the match percentage calculated?", "Multi-factor formula se: 60% Required Skills Fit + 15% Preferred Skills Fit + 15% Experience Fit + 10% Education Fit."),
        ("16. Does the LLM calculate the score?", "No Sir! LLM sirf entities extract karta hai. Scoring calculation 100% deterministic Python formula se hoti hai taaki score har baar consistent aur bias-free rahe."),
        ("17. What database is used?", "Supabase Managed PostgreSQL. Yeh ACID-compliant hai aur semi-structured profile data ke liye JSONB columns support karta hai."),
        ("18. How many tables are in your database?", "Total 8 core tables: profiles, resumes, job_descriptions, candidate_skills, job_skills, analyses, skill_gaps, recommendations (plus audit_logs)."),
        ("19. What is Row Level Security (RLS)?", "PostgreSQL ka security feature jisme har table row par policy lagti hai taaki User A ka data User B na dekh sake."),
        ("20. How is authentication implemented?", "Supabase Auth (JWT tokens) ke zariye. Passwords securely hashed hote hain aur frontend har request me Bearer token bhejta hai."),
        ("21. Where are the secret API keys stored?", "Environment variables (.env file) mein, jo `.gitignore` mein added hain taaki GitHub repository par expose na ho."),
        ("22. What is PII and how does your project protect it?", "Personally Identifiable Information (email, phone number). Humne utility functions banaye hain jo audit logs me email aur phone ko mask (redact) kar dete hain."),
        ("23. What is CORS and how did you configure it?", "Cross-Origin Resource Sharing. FastAPI me CORSMiddleware lagaya hai jo sirf hamari Vercel frontend domain aur localhost ko allow karta hai."),
        ("24. How did you solve Render Free Tier cold-start issue?", "Navbar me auto-retry loop lagaya hai jo first health ping fail hone par 4 times check karta hai jab tak server wake-up na ho jaye, aur click-to-retry button bhi diya hai."),
        ("25. What is Pydantic in FastAPI?", "Data validation aur parsing library. Request aur response bodies ke types enforce karti hai aur invalid data par automatic HTTP 422 deti hai."),
        ("26. How do you verify that matched skills are authentic?", "Backend regex line-search karke resume raw text se exact sentence nikalta hai aur evidence ke roop me report me attach karta hai."),
        ("27. Can a candidate get 100% score without preferred skills?", "Haan Sir, agar job description me preferred skills mention nahi hain, toh system preferred skills ko full credit de deta hai."),
        ("28. What is the difference between GET and POST?", "GET server se data fetch karta hai URL parameters ke through; POST server par data create ya upload karta hai request body ke through."),
        ("29. What is JSON?", "JavaScript Object Notation. Lightweight key-value format jo frontend aur backend ke beech data exchange karne ke liye use hota hai."),
        ("30. What automated tests did you write?", "pytest ke 55 unit aur integration tests likhe hain jo file parsing, security, rate limiting aur scoring logic ko verify karte hain."),
        ("31. Why did you not use Tailwind CSS?", "Vanilla CSS design system banaya hai (`index.css`) custom CSS variables ke sath. Isse complete aesthetic control mila aur zero build-tool bloat raha."),
        ("32. How do you prevent SQL Injection?", "Supabase PostgREST parameter-binding aur Pydantic schemas use kiye hain. Raw SQL concatenation completely avoided hai."),
        ("33. What is Rate Limiting in your project?", "Custom middleware jo har IP address ko 60 requests per minute par restrict karta hai taaki DoS attacks na ho sakein."),
        ("34. What is the role of `skill_normalizer.py`?", "Yeh 300+ skills dictionary ke zariye raw aliases (jaise `JS`, `ES6`) ko standard canonical name (`JavaScript`) me map karta hai."),
        ("35. What is the purpose of `audit_logs` table?", "Har critical event (analysis created, report viewed, resume uploaded) ko user ID aur IP address ke sath track karna compliance ke liye."),
        ("36. What happens if a resume is password-protected?", "PyMuPDF checks `doc.is_encrypted` and raises HTTP 400 Bad Request telling user to upload unprotected file."),
        ("37. Can your system analyze non-IT resumes (like B.Com / BBA)?", "Yes Sir! Finance, Marketing, HR aur Accounting ke 50+ skills mapped hain (Tally, GST, Payroll, Recruitment, etc.)."),
        ("38. What is Vite?", "Modern frontend build tool jo native ES modules aur Rollup use karta hai, jisse hot-module replacement extremely fast hota hai."),
        ("39. What are React Hooks used in your project?", "useState, useEffect, useLocation, useNavigate, aur custom useAuth hook."),
        ("40. What is an SPA (Single Page Application)?", "Aise web app jisme page switch karne par pura browser reload nahi hota, sirf React components dynamically change hote hain."),
        ("41. How does the frontend talk to the backend?", "Axios HTTP client ke through. Base URL automatically production (Render) ya localhost me switch ho jata hai."),
        ("42. What is the role of `uvicorn`?", "FastAPI ke liye high-performance ASGI web server jo Python async code ko run karta hai."),
        ("43. What is the fairness disclaimer in your project?", "Ek automated ethical notice jo batata hai ki score ek analytical indicator hai aur automated hiring rejection nahi hai."),
        ("44. What are the limitations of your project?", "Scanned image OCR abhi integrated nahi hai, language support mostly English hai, aur free-tier hosting par cold-start wake up delay hota hai."),
        ("45. What will you improve in the future?", "Tesseract OCR add karenge scanned PDFs ke liye, recruiter batch processing banayenge (100 resumes ek sath), aur AI mock interview generator add karenge."),
        ("46. What is the difference between a missing skill and an unmentioned skill?", "Recruitment perspective se, agar skill resume me mentioned nahi hai toh employer use missing hi treat karta hai kyunki proof absent hai."),
        ("47. How do you handle multi-column resume layouts?", "PyMuPDF block extraction use karta hai jo columns ko horizontally merge karne ke bajaye vertical reading order maintain karta hai."),
        ("48. Where is your project deployed?", "Frontend Vercel par deployed hai, Backend Render par, aur Database Supabase cloud par."),
        ("49. What was your personal contribution?", "Maine end-to-end full stack architecture design aur code kiya: React 18 UI components, FastAPI REST API routes, PyMuPDF parsing pipeline, Skill Gap detection algorithm, Supabase database schema, aur live deployment on Vercel + Render."),
        ("50. Why should this project get an 'A' grade?", "Kyunki yeh ek working production software hai with live URLs, 55 passing tests, zero-hallucination deterministic scoring, clean database design, aur complete ethical considerations.")
    ]

    for q, a in viva_qas:
        story.append(Paragraph(q, qa_q))
        story.append(Paragraph(a, qa_a))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 8: 15 DIFFICULT / TRAP QUESTIONS
    # =========================================================================
    story.append(Paragraph("CHAPTER 8: 15 Difficult & Trap Viva Questions", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    traps = [
        ("Trap 1: If an LLM is non-deterministic, why does your score never change for the same resume?",
         "Honest Ans: Because the LLM does NOT calculate the score! The LLM only extracts text entities. All mathematical scoring is computed deterministically in Python using our fixed formula."),

        ("Trap 2: Can a candidate trick your system by keyword stuffing in white text?",
         "Honest Ans: PyMuPDF extracts raw character streams regardless of text color. However, because our system requires authentic context sentences (sentence evidence matching) rather than just isolated keywords, isolated stuffed words get lower credibility during parsing."),

        ("Trap 3: Why didn't you use LangChain or LlamaIndex?",
         "Honest Ans: LangChain adds unnecessary abstraction and dependency bloat for a focused task. Direct integration with the official OpenAI SDK using structured Pydantic JSON mode gives us faster execution, lower memory overhead, and 100% control over error handling."),

        ("Trap 4: Why 60% for required skills and not 50% or 70%?",
         "Honest Ans: In technical recruitment, required skills are mandatory deal-breakers (60% weight). Experience depth (15%), bonus preferred skills (15%), and degree alignment (10%) provide balanced holistic evaluation without overshadowing technical competency."),

        ("Trap 5: What is the exact difference between candidate_skills and job_skills tables?",
         "Honest Ans: `candidate_skills` stores skills extracted from a specific candidate resume linked via `resume_id`. `job_skills` stores criteria from a target job description linked via `job_id` with `requirement_type` ('required' vs 'preferred') and `importance_weight`."),

        ("Trap 6: How do you handle false skill matches (e.g. candidate worked at 'Amazon' vs candidate knows 'Amazon Web Services')?",
         "Honest Ans: In our canonical dictionary, 'AWS' and 'Amazon Web Services' are mapped strictly to cloud computing. Company names are parsed into the `experience.company` entity field by the LLM prompt, separating employer names from technical competencies."),

        ("Trap 7: What happens if a candidate uploads an empty 0-byte file?",
         "Honest Ans: In `file_validation.py`, we check `len(file_bytes) == 0` and immediately raise HTTP 400 Bad Request: 'Uploaded file is empty.'"),

        ("Trap 8: How do you ensure candidate data privacy under GDPR/data protection norms?",
         "Honest Ans: We implement PII redaction in audit logs, enforce PostgreSQL Row Level Security (RLS) so users only see their own resumes, and provide a direct `DELETE /api/analysis/{id}` endpoint allowing users to purge their records."),

        ("Trap 9: What is the difference between JSON and JSONB in PostgreSQL?",
         "Honest Ans: Plain JSON stores raw text which must be re-parsed on every query. JSONB stores decomposed binary format which supports indexing (GIN indexes), faster key-value lookups, and query operations inside nested JSON structures."),

        ("Trap 10: Why did you deploy frontend and backend on two different platforms (Vercel & Render)?",
         "Honest Ans: Separation of Concerns. Vercel is optimized for static assets and client-side SPA routing via Edge CDNs, while Render provides a dedicated long-running Python 3.13 Linux container for heavy computational tasks like PyMuPDF extraction."),

        ("Trap 11: How do you verify that your API is running without opening the frontend?",
         "Honest Ans: By accessing `https://ai-resume-backend-61zn.onrender.com/api/health` which returns `{\"status\":\"healthy\",\"database\":\"connected\"}`, or visiting `/docs` for the interactive Swagger UI."),

        ("Trap 12: How do you handle candidates who mention skills indirectly (e.g., 'Built microservices with containerization')?",
         "Honest Ans: The LLM prompt understands semantic context and extracts 'Microservices' and 'Containerization'. Then our transferable clusters map 'Containerization' to 'Docker' and 'Kubernetes' with partial credit."),

        ("Trap 13: What happens if the database connection drops during an analysis?",
         "Honest Ans: Our `SupabaseService` wraps database calls in try-except blocks. If persistence fails, the backend still returns the computed in-memory analysis report to the frontend and logs an error, ensuring the candidate sees their result."),

        ("Trap 14: What is the execution time of a single resume analysis?",
         "Honest Ans: Approximately 2.5 to 4 seconds total: ~200ms for PyMuPDF text extraction, ~1.8s for OpenAI structured JSON response, ~50ms for Python scoring, and ~400ms for Supabase database insertion."),

        ("Trap 15: What is the most important lesson you learned building this project?",
         "Honest Ans: That in production AI engineering, the LLM is only a small component. The real value lies in building deterministic guardrails, clean normalization taxonomies, defensive error fallbacks, and intuitive user experiences around the AI.")
    ]

    for q, a in traps:
        story.append(Paragraph(q, qa_q))
        story.append(Paragraph(a, qa_a))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 9: LAST-MINUTE 5-MINUTE REVISION
    # =========================================================================
    story.append(Paragraph("CHAPTER 9: Last-Minute 5-Minute Viva Revision Sheet", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6366f1'), spaceAfter=5))

    top10_list = [
        "1. <b>Project Title:</b> AI-Powered Resume Analysis API with Skill Gap Detection using LLMs.",
        "2. <b>Live URLs:</b> Frontend on Vercel, Backend on Render, Database on Supabase.",
        "3. <b>AI Model:</b> OpenAI <code>gpt-4o-mini</code> (JSON schema mode) + Intelligent Heuristic Regex Fallback.",
        "4. <b>Scoring Formula:</b> 60% Required Skills + 15% Preferred + 15% Experience + 10% Education.",
        "5. <b>Transferable Skills:</b> Adjacent skills get 50% partial credit (e.g. Django for FastAPI).",
        "6. <b>PDF Parser:</b> PyMuPDF (fitz) with $<40$ characters scanned document rejection safeguard.",
        "7. <b>Word Parser:</b> python-docx extracting paragraphs and resume table columns.",
        "8. <b>Security Controls:</b> Supabase RLS, JWT Auth, PII Masking, Rate Limiting (60 req/min), CORS Whitelist.",
        "9. <b>Test Suite:</b> 55 / 55 tests passed cleanly with pytest.",
        "10. <b>Database Tables:</b> profiles, resumes, job_descriptions, candidate_skills, job_skills, analyses, skill_gaps, recommendations, audit_logs.",
    ]
    for item in top10_list:
        story.append(Paragraph(item, bullet_style))

    story.append(Spacer(1, 10))
    final_note = (
        "<b>FINAL CONFIDENCE MANTRA:</b><br/>"
        "Examiner ke saamne smile ke sath confident rehna. "
        "Aapka project 100% real hai, working live URL par hosted hai, 55 automated tests se backed hai, "
        "aur aapke paas har mathematical calculation ka logic ready hai. You will definitely score an A+ grade!"
    )
    story.append(callout("ALL THE VERY BEST FOR YOUR VIVA!", final_note, "#4338ca", "#eef2ff", base_styles))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated Comprehensive Master Viva Manual: {output_filename}")


if __name__ == "__main__":
    out_pdf = os.path.join(os.path.abspath(os.path.dirname(__file__)), "BSc_IT_Final_Viva_Master_Handbook_Hinglish.pdf")
    build_master_viva_manual(out_pdf)
