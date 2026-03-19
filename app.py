import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8005"

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# ---------------- SESSION STATE ----------------
for key in ["messages", "session_id", "sessions"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "messages" else None

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Setup")

# Create User
st.sidebar.subheader("👤 Create User")
name = st.sidebar.text_input("Enter Name")

if st.sidebar.button("Create User"):
    if name:
        res = requests.post(f"{BASE_URL}/user/", params={"name": name})
        if res.status_code == 200:
            data = res.json()
            st.sidebar.success(f"User ID: {data['id']}")
        else:
            st.sidebar.error(res.text)

# Create Session
st.sidebar.subheader("💬 Create Session")
user_id = st.sidebar.number_input("User ID", step=1)

if st.sidebar.button("Create Session"):
    if user_id <= 0:
        st.sidebar.error("Invalid User ID")
    else:
        res = requests.post(f"{BASE_URL}/session/", params={"user_id": user_id})
        if res.status_code == 200:
            data = res.json()
            if "result" in data:
                st.sidebar.error(data["result"])
            else:
                st.session_state.session_id = data["id"]
                st.sidebar.success(f"Session ID: {data['id']}")
        else:
            st.sidebar.error(res.text)

# Load Sessions
st.sidebar.subheader("📂 Load Sessions")
load_user_id = st.sidebar.number_input("User ID", step=1, key="load")

if st.sidebar.button("Load Sessions"):
    if load_user_id <= 0:
        st.sidebar.error("Invalid User ID")
    else:
        res = requests.get(f"{BASE_URL}/usersessions", params={"user_id": load_user_id})
        if res.status_code == 200:
            data = res.json()
            st.session_state.sessions = data["sessions"]
            st.sidebar.success("Loaded")
        else:
            st.sidebar.error(res.text)

# Session Selector
if st.session_state.sessions:
    session_ids = [s["session_id"] for s in st.session_state.sessions]
    selected_session = st.sidebar.selectbox("Select Session", session_ids)
    st.session_state.session_id = selected_session

    if st.sidebar.button("Load Chat"):
        st.session_state.messages = []
        for s in st.session_state.sessions:
            if s["session_id"] == selected_session:
                for chat in s["chats"]:
                    st.session_state.messages.append({"role": "user", "content": chat["query"]})
                    st.session_state.messages.append({"role": "assistant", "content": chat["response"]})

# ---------------- MAIN UI ----------------
st.title("🤖 Smart AI Chatbot")

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
prompt = st.chat_input("Type your message...")

if prompt:
    if not st.session_state.session_id:
        st.warning("Create or select a session")
    else:
        # show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # streaming effect placeholder
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            with st.spinner("Thinking..."):
                res = requests.post(
                    f"{BASE_URL}/chat/",
                    params={"session_id": st.session_state.session_id, "query": prompt}
                )

            if res.status_code == 200:
                reply = res.json().get("result", "")

                # typing effect
                for word in reply.split():
                    full_response += word + " "
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(res.text)
