# Imports
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import docx2txt
import pdfplumber
import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from streamlit_option_menu import option_menu

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("C:\\Users\\Gagan\\OneDrive\\Desktop\\career_guru_stream\\careerguru-f1540-firebase-adminsdk-fbsvc-e0a2a00921.json")  # Path to your Firebase service account key
    firebase_admin.initialize_app(cred)
db = firestore.client()

# UI Theme Colors
PRIMARY_COLOR = "#0D1B2A"  # Sapphire
SECONDARY_COLOR = "#F4B400"  # Dandelion

st.set_page_config(page_title="Career Guru", layout="wide")
st.markdown(
    f"""
    <style>
        body {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        .block-container {{
            padding: 2rem;
        }}
        .stButton>button {{
            background-color: {SECONDARY_COLOR};
            color: {PRIMARY_COLOR};
            font-weight: bold;
            border-radius: 8px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Global State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# Authentication Functions
def register_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({"email": email, "chat_history": []})
        return True, "Registered successfully."
    except Exception as e:
        return False, str(e)

def login_user(email, password):
    users = db.collection("users").where("email", "==", email).stream()
    for u in users:
        st.session_state.authenticated = True
        st.session_state.user = u.id
        return True, "Logged in successfully."
    return False, "Invalid credentials or user not found."

# Landing Page: Login/Register
if not st.session_state.authenticated:
    st.title("Career Guru")
    choice = st.radio("Choose an option", ["Login", "Register"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            success, msg = login_user(email, password)
            if success:
                st.success(msg)
                st.rerun()  # ← Add this line
            else:
                st.error(msg)
    else:
        if st.button("Register"):
            success, msg = register_user(email, password)
            if success:
                st.success(msg)
                st.rerun()  # ← Add this line
            else:
                st.error(msg)


else:
    # LLM
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    if not GROQ_API_KEY:
        st.error("Please add your GROQ_API_KEY to .streamlit/secrets.toml")
        st.stop()

    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192", temperature=0.7)

    # Sidebar Navigation
    with st.sidebar:
        selected = option_menu(
            menu_title=None,
            options=["Mock Interview", "Career Explorer", "Resume Analyzer", "About Us", "Logout"],
            icons=["mic", "search", "file-earmark-text", "info-circle", "box-arrow-left"],
            menu_icon="list",
            default_index=0,
        )

    # Logout
    if selected == "Logout":
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    # 1. Mock Interview
    if selected == "Mock Interview":
        st.subheader("🎯 AI Mock Interview Coach")
        role = st.text_input("Enter your desired job role:")
        prep = st.text_area("Describe your preparation strategy:")
        question = st.text_input("Ask a mock interview question:")

        if role and prep and question:
            template = PromptTemplate(
                input_variables=["role", "prep", "input"],
                template="""You are a helpful AI career coach.
                The user wants to get a job as a {role} and is preparing with: {prep}.
                Engage in a mock interview.
                User: {input}
                AI:"""
            )
            formatted_prompt = template.format(role=role, prep=prep, input=question)
            response = llm.invoke(formatted_prompt).content
            st.markdown(f"**You:** {question}")
            st.markdown(f"**Coach:** {response}")

            db.collection("users").document(st.session_state.user).update({
                "chat_history": firestore.ArrayUnion([{"q": question, "a": response}])
            })

    # 2. Career Explorer
    elif selected == "Career Explorer":
        st.subheader("🔍 Career Exploration Assistant")
        explorer_role = st.text_input("Enter a job role to explore:")
        question = st.text_input("Ask a question about this role:")

        if explorer_role and question:
            prompt = f"""
            You are a career guidance AI. The user is interested in the role: '{explorer_role}'.
            Question: '{question}'
            Provide a helpful answer.
            """
            result = llm.invoke(prompt).content
            st.markdown(f"**You:** {question}")
            st.markdown(f"**Career Guru:** {result}")

    # 3. Resume Analyzer
    elif selected == "Resume Analyzer":
        st.subheader("📄 Resume Analyzer")
        uploaded_file = st.file_uploader("Upload your resume (PDF/DOCX)", type=["pdf", "docx"])
        text = ""

        if uploaded_file:
            ext = uploaded_file.name.split('.')[-1]
            if ext == "pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            elif ext == "docx":
                text = docx2txt.process(uploaded_file)

            if text:
                resume_prompt = f"""
                You are a resume reviewer AI. Analyze this resume and give feedback:
                - Clarity, formatting
                - Strengths
                - Relevance to tech roles
                - Suggestions
                Resume: {text}
                """
                feedback = llm.invoke(resume_prompt).content
                st.markdown("### 🔍 Feedback")
                st.markdown(feedback)
            else:
                st.error("Could not extract text.")

    # 4. About Us
    elif selected == "About Us":
        st.subheader("ℹ️ About Career Guru")
        st.markdown(f"""
            <div style='color: white;'>
            <p><strong>Career Guru</strong> is an AI-powered career assistant platform using:</p>
            <ul>
                <li>LLaMA 3 via Groq API</li>
                <li>LangChain for prompt engineering</li>
                <li>Streamlit with Firebase integration</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"<hr><center style='color: white;'>© 2025 Career Guru</center>", unsafe_allow_html=True)
