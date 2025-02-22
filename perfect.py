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

# Define conversation steps (Integrated into AI's response)
steps = [
    "Do you outsource campaign management?",
    "What industries do you target?",
    "What kind of results are you expecting?",
    "What challenges do you face in your campaigns?",
    "What is your payout per sale?",
    "What is your payout duration? Weekly or monthly?",
    "Let's schedule a call. What time works for you?"
]

# Initialize session state for chat management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # Dictionary to store multiple clients' chat history
if "selected_client" not in st.session_state:
    st.session_state.selected_client = None  # Currently selected client
if "step_index" not in st.session_state:
    st.session_state.step_index = {}  # Track steps for each client separately

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
            st.session_state.step_index[new_client_name] = 0  # Start from first question
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

    # Ensure the step index is initialized for the client
    if client_name not in st.session_state.step_index:
        st.session_state.step_index[client_name] = 0  # Start from first question

    # If conversation is empty, start with greeting message
    if not st.session_state.chat_history[client_name]:
        greeting_message = f"Hello {client_name},\n\nI hope you're doing well! We at Ethnotec specialize in campaign management. {steps[0]}"
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
        - Respond in a human-like, professional, and direct manner.
        - Do NOT list steps separately. Instead, integrate the next question naturally into your response.
        - If the user asks an unrelated question, answer briefly but return to the main flow.
        - Make sure your response acknowledges the user's answer and smoothly transitions into the next step."""

        # Determine next step
        if st.session_state.step_index[client_name] < len(steps) - 1:
            next_step = steps[st.session_state.step_index[client_name] + 1]
            st.session_state.step_index[client_name] += 1
        else:
            next_step = "Thanks for the discussion! Looking forward to working together."

        # Generate AI-enhanced response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}]
            + st.session_state.chat_history[client_name]
        )

        ai_reply = response.choices[0].message.content

        # Combine AI response with the next question smoothly
        final_reply = f"{ai_reply} {next_step}"

        # Add AI response + next question to conversation
        st.session_state.chat_history[client_name].append({"role": "assistant", "content": final_reply})
        st.chat_message("assistant").write(final_reply)
