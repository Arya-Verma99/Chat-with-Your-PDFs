import os
import re
import streamlit as st
from core.vectorstore_manager import PDFVectorStoreManager
from core.chat_groq import ChatWithGroq
from core.history_manager import ChatHistoryManager

st.set_page_config(page_title="ChatPDF with Groq", layout="wide")

# --- Initialize memory ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "chatbot_context" not in st.session_state:
    st.session_state["chatbot_context"] = None
if "selected_history" not in st.session_state:
    st.session_state["selected_history"] = "New Session"
if "active_session_id" not in st.session_state:
    st.session_state["active_session_id"] = "New Session"
if "last_uploaded_files" not in st.session_state:
    st.session_state["last_uploaded_files"] = []
# Handle session switch or uploaded files to reset chatbot context
if "file_uploader_key" not in st.session_state:
    st.session_state.file_uploader_key = "file_uploader_0"
# When resetting (new chat or session change), increment key to reset uploader
def reset_uploader():
    if "file_uploader_key" in st.session_state:
        # Increment key to force Streamlit reset file uploader
        key_number = int(st.session_state.file_uploader_key.split("_")[-1])
        st.session_state.file_uploader_key = f"file_uploader_{key_number + 1}"
    else:
        st.session_state.file_uploader_key = "file_uploader_0"

# --- Login: Enter Groq API Key ---
if "groq_api_key" not in st.session_state:
    st.title("🔐 Login to ChatPDF")
    api_key = st.text_input("Enter your Groq API Key", type="password")
    if st.button("Login"):
        if api_key.startswith("gsk_"):
            st.session_state["groq_api_key"] = api_key
            st.rerun()
        else:
            st.error("Please enter a valid Groq API key.")
    st.stop()

# --- Managers ---
vector_manager = PDFVectorStoreManager()
history_manager = ChatHistoryManager()

# --- App Title ---
st.title("📄 Chat with Your PDFs using Groq + LangChain")

# --- Sidebar: Load old sessions ---
with st.sidebar:
    st.header("📜 Chat Sessions")
    if st.button("➕ New Chat", use_container_width=True):
       # Save current chat session before reset
       if st.session_state.get("chat_history"):
           history_manager.history = st.session_state["chat_history"]
           saved_path = history_manager.save()
           st.toast(f"Previous session saved to: {saved_path}")
       # Reset state for new session
       st.session_state["chat_history"] = []
       st.session_state["chatbot_context"] = None
       st.session_state["selected_history"] = "New Session"
       st.session_state["active_session_id"] = "New Session"
       st.session_state["last_uploaded_files"] = []
       reset_uploader()
       st.rerun()
    try:
        history_files = [f for f in os.listdir("chat_history") if f.endswith(".json")]
    except FileNotFoundError:
        history_files = []

    selected_history = st.selectbox("Choose Session", ["New Session"] + history_files)
    st.session_state["selected_history"] = selected_history


uploaded_files = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True, key=st.session_state.file_uploader_key)
file_names = [f.name for f in uploaded_files] if uploaded_files else []

# Detect state switch or new document upload
session_changed = st.session_state["selected_history"] != st.session_state["active_session_id"]
file_changed = file_names != st.session_state["last_uploaded_files"]

if session_changed or file_changed:
    st.session_state["chatbot_context"] = None
    st.session_state["chat_history"] = []
    st.session_state["last_uploaded_files"] = file_names
    st.session_state["active_session_id"] = st.session_state["selected_history"]

# --- Load selected chat history if needed ---
if st.session_state["selected_history"] != "New Session":
    session_name = st.session_state["selected_history"].replace(".json", "")
    loaded_history = history_manager.load(session_name)
    st.session_state["chat_history"] = loaded_history
    st.session_state["chatbot_context"] = None

# --- Create new chatbot if needed ---
if st.session_state["selected_history"] == "New Session" and uploaded_files:
    if st.session_state["chatbot_context"] is None:
        with st.spinner("📖 Reading and indexing documents..."):
            retriever = vector_manager.create_or_load_vectorstore(uploaded_files)
            chatbot = ChatWithGroq(retriever, groq_api_key=st.session_state["groq_api_key"])
            st.session_state["chatbot_context"] = chatbot


# --- Chat Block ---
chatbot = st.session_state.get("chatbot_context", None)

if chatbot and st.session_state["selected_history"] == "New Session":
    user_question = st.chat_input("Ask something about your PDFs...")

    if user_question:
        with st.spinner("💡 Thinking..."):
            response = chatbot.ask(user_question)
            raw_answer = response["answer"]
            think_match = re.search(r"<think>(.*?)</think>", raw_answer, re.DOTALL | re.IGNORECASE)
            if think_match:
                reasoning = think_match.group(1).strip()
                final_answer = re.sub(r"<think>.*?</think>", "", raw_answer, flags=re.DOTALL | re.IGNORECASE).strip()
            else:
                reasoning = None
                final_answer = raw_answer.strip()

            st.session_state["chat_history"].append({
                "user": user_question,
                "bot": raw_answer,
                "reasoning": reasoning,
                "answer": final_answer
            })

# --- Display chat history ---
if st.session_state.get("chat_history"):
    for msg in st.session_state["chat_history"]:
        print(msg.get("reasoning"))
        with st.chat_message("user"):
            st.markdown(msg["user"])
        with st.chat_message("assistant"):
            if msg.get("reasoning"):
                with st.expander("🧠 LLM Thinking", expanded=False):
                    st.markdown(f"{msg.get("reasoning") or 'No reasoning provided.'}")
            st.markdown(msg.get("answer") or msg["bot"])


# --- Save session ---
if st.session_state["selected_history"] == "New Session" and st.session_state["chat_history"]:
    st.markdown("---")
    st.subheader("💾 Save this session")

    custom_name = st.text_input("Optional filename (e.g. receipts.json):", key="save_name")

    if st.button("✅ Save Chat", use_container_width=True):
        filename = custom_name.strip() if custom_name.endswith(".json") else None
        history_manager.history = st.session_state["chat_history"]
        path = history_manager.save(name=filename)
        st.success(f"📁 Session saved to `{path}`")