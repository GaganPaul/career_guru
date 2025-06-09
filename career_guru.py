import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Load API key from Streamlit secrets.toml
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

# Check API key
if not GROQ_API_KEY:
    st.error("Please add your GROQ_API_KEY to Streamlit secrets.toml.")
    st.stop()

# Set up LangChain LLM with model
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama3-8b-8192",  # or omit if unsure
    temperature=0.7
)

memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory, verbose=False)

# Streamlit UI Configuration
st.set_page_config(page_title="Career Guru", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0f1117;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.chat-box {
    background-color: #1a1d29;
    border-radius: 16px;
    padding: 15px 20px;
    box-shadow: 0 0 12px #5f5fff22;
    margin-bottom: 12px;
    max-width: 75%;
    word-wrap: break-word;
}
.user {
    background-color: #3b82f6;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 0;
}
.bot {
    background-color: #272b43;
    color: white;
    align-self: flex-start;
    border-bottom-left-radius: 0;
}
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("Career Guru")
st.subheader("Polish your answers. Level up your confidence.")

# Initialize session state to hold chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input Box
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("🗨️ Ask your interview question or simulate an HR round:")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    # Get bot response
    response = conversation.predict(input=user_input)

    # Append user and bot messages to history
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", response))

# Display chat history in chat bubbles
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for speaker, message in st.session_state.chat_history:
    css_class = "user chat-box" if speaker == "user" else "bot chat-box"
    st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""<hr style="border: 0.5px solid #333">""", unsafe_allow_html=True)
#st.markdown("""<p style='text-align: center; font-size: small;'>Built with ❤️ using LangChain, Groq & Streamlit</p>""", unsafe_allow_html=True)
