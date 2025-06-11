import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import docx2txt
import pdfplumber
import os

# ---------- Setup ----------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Please add your GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192", temperature=0.7)

# ---------- Layout ----------
st.set_page_config(page_title="Career Guru", layout="wide")
st.markdown("<h1 style='text-align: center;'>💼 Career Guru</h1>", unsafe_allow_html=True)

# ---------- Tabs ----------
tabs = st.tabs(["🎙️ Mock Interview", "🧭 Career Explorer", "📄 Resume Analyzer", "ℹ️ About Us"])

# ---------- 1. Mock Interview Tab ----------
with tabs[0]:
    st.subheader("🎯 AI Mock Interview Coach")

    if "mock_history" not in st.session_state:
        st.session_state.mock_history = []

    role = st.text_input("Enter your desired job role:", key="mock_role")
    prep = st.text_area("Describe your preparation strategy:", key="mock_prep")
    question = st.text_input("Ask an interview question or simulate an HR round:", key="mock_q")

    if role and prep and question:
        template = PromptTemplate(
            input_variables=["role", "prep", "input"],
            template="""You are a helpful AI career coach.
            The user wants to get a job as a {role} and is preparing with the following approach: {prep}.
            Engage in a mock interview session.
            User: {input}
            AI:"""
        )
        formatted_prompt = template.format(role=role, prep=prep, input=question)
        response = llm.invoke(formatted_prompt).content
        st.session_state.mock_history.append(("You", question))
        st.session_state.mock_history.append(("Coach", response))

    for speaker, msg in st.session_state.mock_history:
        st.markdown(f"**{speaker}:** {msg}")

# ---------- 2. Career Explorer Tab ----------
with tabs[1]:
    st.subheader("🔍 Career Exploration Assistant")

    if "explore_role" not in st.session_state:
        st.session_state.explore_role = ""
    if "career_qna" not in st.session_state:
        st.session_state.career_qna = []

    explorer_role = st.text_input("Enter a job role or career field you're interested in exploring:", value=st.session_state.explore_role, key="explore_role_input")

    if explorer_role:
        st.session_state.explore_role = explorer_role
        st.success(f"You're exploring: {st.session_state.explore_role}")

        question = st.text_input("Ask something about this role (e.g., required skills, salary, courses):", key="explore_question")

        if question:
            career_prompt = f"""
            You are a career guidance AI. The user is interested in the career path of a '{st.session_state['explore_role']}'.
            They have this question: "{question}"
            Provide a detailed and helpful answer with examples and resources if applicable.
            Provide detailed insights on:
            - Key responsibilities
            - Required skills and qualifications
            - Growth opportunities
            - Common industries
            - Career tips and paths
            - Certifications or courses (if any), if asked
            """
            result = llm.invoke(career_prompt).content
            st.session_state.career_qna.append(("You", question))
            st.session_state.career_qna.append(("Career Guru", result))

    if st.session_state.explore_role:
        for speaker, msg in st.session_state.career_qna:
            st.markdown(f"**{speaker}:** {msg}")
    else:
        st.info("Please enter a career field to begin exploring.")

# ---------- 3. Resume Analyzer Tab ----------
with tabs[2]:
    st.subheader("📄 Resume Analyzer")

    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file:
        ext = uploaded_file.name.split('.')[-1]
        text = ""

        if ext == "pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif ext == "docx":
            text = docx2txt.process(uploaded_file)

        if text:
            st.success("Resume content extracted successfully!")
            resume_prompt = f"""
            You are a resume reviewer AI. Analyze the following resume content and give feedback on:
            - Clarity and formatting
            - Strength of the experience and skills
            - Relevance to tech roles
            - Suggested improvements
            Resume Content:
            {text}
            """
            feedback = llm.invoke(resume_prompt).content
            st.markdown("### 🔍 Resume Feedback")
            st.markdown(feedback)
        else:
            st.error("Could not extract text from the uploaded file.")

# ---------- 4. About Us Tab ----------
with tabs[3]:
    st.subheader("ℹ️ About Career Guru")
    st.markdown("""
    **Career Guru** is an AI-powered career assistant built using:

    - 🧠 LLaMA 3 via Groq API for lightning-fast responses
    - 🔗 LangChain for chaining intelligent prompts
    - 🌐 Streamlit for a sleek, interactive web UI

    Whether you're exploring career paths, preparing for interviews, or reviewing your resume — Career Guru is here to empower your journey.

    
    """)

# ---------- Footer ----------
st.markdown("<hr><center>© 2025 Career Guru</center>",
            unsafe_allow_html=True)
#