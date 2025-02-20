import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Streamlit UI
st.set_page_config(layout="wide")  # Wide layout for better UI
st.title("🤖 Ethnotec Business Chatbot")
st.write("This chatbot helps you interact with potential clients about campaign outsourcing.")

# Initialize session state for chat management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # Dictionary to store multiple clients' chat history
if "selected_client" not in st.session_state:
    st.session_state.selected_client = None  # Currently selected client

# Sidebar: Client List & New Client Creation
st.sidebar.title("📋 Manage Clients")

# Add new client directly from sidebar
new_client_name = st.sidebar.text_input("Enter new client name:", "")

if st.sidebar.button("➕ Add Client"):
    if new_client_name.strip():  # Ensure it's not empty
        if new_client_name in st.session_state.chat_history:
            st.sidebar.warning("Client already exists! Choose another name.")
        else:
            st.session_state.chat_history[new_client_name] = []
            st.session_state.selected_client = new_client_name
            st.sidebar.success(f"Client '{new_client_name}' added!")

# Display existing clients
if st.session_state.chat_history:
    client_list = list(st.session_state.chat_history.keys())
    selected_client = st.sidebar.radio("Select a Client:", client_list, index=0)

    # If a different client is selected, update session state
    if selected_client != st.session_state.selected_client:
        st.session_state.selected_client = selected_client

# Display chat only if a client is selected
if st.session_state.selected_client:
    client_name = st.session_state.selected_client
    st.subheader(f"💬 Chat with {client_name}")

    # If conversation is empty, start with greeting message
    if not st.session_state.chat_history[client_name]:
        greeting_message = f"Hello {client_name},\n\nI hope you're doing well! We at Ethnotec specialize in campaign management. Do you outsource campaign management?"
        st.session_state.chat_history[client_name].append({"role": "assistant", "content": greeting_message})

    # Display chat history
    for chat in st.session_state.chat_history[client_name]:
        if chat["role"] == "assistant":
            st.chat_message("assistant").write(chat["content"])
        else:
            st.chat_message("user").write(chat["content"])

    # User input (Client Response)
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add client response to conversation history
        st.session_state.chat_history[client_name].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # AI System Prompt (Keeps AI focused on structured questioning naturally)
        system_prompt = f"""You are a professional business representative from Ethnotec.
Your task is to have a structured, natural, and professional conversation with potential clients.

### **Start of Conversation:**
- The conversation **must always begin with**:
  "Hello {{client_name}},\n\nI hope you're doing well! We at Ethnotec specialize in campaign management. Do you outsource campaign management?"

### **Core Questions (To be asked one by one based on user responses):**
1. What industries do you target?
2. What kind of results are you expecting?
3. What challenges do you face in your campaigns?
4. What is your payout per sale?
5. What is your payout duration? Weekly or monthly?
6. Let's schedule a call. What time works for you?

### **Rules for Response Generation:**
- After the first question, analyze the user's response and ask the next most relevant question.
- Always acknowledge the user's response before smoothly transitioning to the next question.
- If the user **answers multiple questions at once**, intelligently **skip already answered questions** and move to the next relevant one.
- If the user asks an **unrelated question**, give a **short, polite answer** but quickly **redirect the conversation back to the campaign outsourcing discussion**.
- Avoid robotic replies and unnecessary details. Keep responses **short, clear, and professional**.
- If the conversation reaches a natural conclusion, suggest scheduling a call.

Make sure the conversation feels **engaging, professional, and natural** while keeping the discussion **goal-oriented**.
"""


        # Generate AI-enhanced response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.chat_history[client_name]
        )

        ai_reply = response.choices[0].message.content

        # Add AI response to conversation
        st.session_state.chat_history[client_name].append({"role": "assistant", "content": ai_reply})
        st.chat_message("assistant").write(ai_reply)
