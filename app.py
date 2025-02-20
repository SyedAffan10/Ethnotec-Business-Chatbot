import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Streamlit UI
st.title("🤖 Ethnotec Business Chatbot")
st.write("This chatbot helps you interact with potential clients about campaign outsourcing.")

# Get client name input
client_name = st.text_input("Enter Client Name:", "")

# Define conversation steps
steps = [
    "Does your company outsource campaign management?",
    "Great! Could you share some details about your current campaigns? Specifically, what industries do you target, and what kind of results are you expecting?",
    "Got it! Based on your campaigns, what kind of challenges do you face? Are you looking for any specific improvements?",
    "Let's talk about payouts. How much do you offer per sale?",
    "If you have a set payout duration, please let us know. If not, do you follow a weekly or monthly payout system?",
    "Let's schedule a quick call to discuss this further. What time works best for you?"
]

# Initialize session state for conversation tracking
if "conversation" not in st.session_state:
    st.session_state.conversation = []
    st.session_state.step_index = 0  # Track conversation step

# If client name is entered, start conversation
if client_name:
    if not st.session_state.conversation:
        greeting_message = f"Hello {client_name},\n\nI hope you're doing well! I'm reaching out from Ethnotec. We specialize in handling and managing marketing campaigns efficiently.\n\n{steps[0]}"
        st.session_state.conversation.append({"role": "assistant", "content": greeting_message})

    # Display chat history
    for chat in st.session_state.conversation:
        if chat["role"] == "assistant":
            st.chat_message("assistant").write(chat["content"])
        else:
            st.chat_message("user").write(chat["content"])

    # User input (Client Response)
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add client response to conversation history
        st.session_state.conversation.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Move to next step based on client response
        if st.session_state.step_index < len(steps) - 1:
            st.session_state.step_index += 1
            next_message = steps[st.session_state.step_index]
        else:
            next_message = "Thank you for the discussion! Looking forward to working together."

        # Generate AI-enhanced response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional business representative from Ethnotec, engaging in a step-by-step conversation with a potential client about outsourcing marketing campaigns."}
            ] + st.session_state.conversation
        )

        ai_reply = response.choices[0].message.content
        final_reply = f"{ai_reply}\n\n{next_message}"

        # Add AI response + next question to conversation
        st.session_state.conversation.append({"role": "assistant", "content": final_reply})
        st.chat_message("assistant").write(final_reply)
