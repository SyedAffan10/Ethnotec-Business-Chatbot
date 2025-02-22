import os
import sqlite3
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import pyperclip
pyperclip.set_clipboard("windows")


# Load API Key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Database Initialization
DB_FILE = "clients.db"

def create_database():
    """Creates necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create clients table
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE)''')

    # Create chat history table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 client_name TEXT,
                 role TEXT,
                 content TEXT,
                 FOREIGN KEY(client_name) REFERENCES clients(name))''')

    conn.commit()
    conn.close()

def add_client_to_db(client_name):
    """Adds a new client to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO clients (name) VALUES (?)", (client_name,))
        conn.commit()
        st.sidebar.success(f"Client '{client_name}' added!")
    except sqlite3.IntegrityError:
        st.sidebar.warning("Client already exists!")
    conn.close()

def delete_client(client_name):
    """Deletes a client and their chat history."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE client_name = ?", (client_name,))
    c.execute("DELETE FROM clients WHERE name = ?", (client_name,))
    conn.commit()
    conn.close()
    st.sidebar.warning(f"Client '{client_name}' deleted!")

def rename_client(old_name, new_name):
    """Renames a client and updates chat history."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE clients SET name = ? WHERE name = ?", (new_name, old_name))
        c.execute("UPDATE chat_history SET client_name = ? WHERE client_name = ?", (new_name, old_name))
        conn.commit()
        st.sidebar.success(f"Client '{old_name}' renamed to '{new_name}'!")
    except sqlite3.IntegrityError:
        st.sidebar.warning("Client name already exists! Choose another name.")
    conn.close()

def get_clients():
    """Fetches all clients from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM clients")
    clients = [row[0] for row in c.fetchall()]
    conn.close()
    return clients

def save_message(client_name, role, content):
    """Saves a message to the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (client_name, role, content) VALUES (?, ?, ?)",
              (client_name, role, content))
    conn.commit()
    conn.close()

def get_chat_history(client_name):
    """Retrieves chat history for a client."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE client_name = ?", (client_name,))
    history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return history

# Initialize database
create_database()

# Streamlit UI
st.set_page_config(layout="wide")  # Wide layout for better UI
st.title("🤖 Ethnotec Business Chatbot")
st.write("This chatbot helps you interact with potential clients about campaign outsourcing.")

# Sidebar: Client List & New Client Creation
st.sidebar.title("📋 Manage Clients")

# Add new client directly from sidebar
new_client_name = st.sidebar.text_input("Enter new client name:", "")

if st.sidebar.button("➕ Add Client"):
    if new_client_name.strip():  # Ensure it's not empty
        add_client_to_db(new_client_name)

# Fetch existing clients from database
clients = get_clients()
selected_client = None

if clients:
    selected_client = st.sidebar.radio("Select a Client:", clients, index=0)

    # Delete Client Button
    if st.sidebar.button("🗑️ Delete Client"):
        delete_client(selected_client)
        st.rerun()

    # Rename Client
    new_name = st.sidebar.text_input("Rename Client:", selected_client)
    if st.sidebar.button("✏️ Rename"):
        if new_name.strip() and new_name != selected_client:
            rename_client(selected_client, new_name)
            st.rerun()

# Display chat only if a client is selected
if selected_client:
    st.subheader(f"💬 Chat with {selected_client}")

    # Fetch chat history from database
    chat_history = get_chat_history(selected_client)

    # If conversation is empty, start with greeting message
    if not chat_history:
        greeting_message = f"Hello {selected_client},\n\nI hope you're doing well! We at Ethnotec specialize in campaign management. Do you outsource campaign management?"
        save_message(selected_client, "assistant", greeting_message)
        chat_history.append({"role": "assistant", "content": greeting_message})


    for chat in chat_history:
        col1, col2 = st.columns([8, 1])
        with col1:
            st.chat_message(chat["role"]).write(chat["content"])

        with col2:
            if chat["role"] == "assistant":  # Only add copy button for AI responses
                copy_text = chat["content"]
                if st.button(f"📋 Copy", key=f"copy_{chat['content']}"):
                    pyperclip.copy(copy_text)  # Copies text to clipboard
                    st.success("Copied to clipboard!")


    # User input (Client Response)
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add client response to conversation history
        save_message(selected_client, "user", user_input)
        st.chat_message("user").write(user_input)

        # AI System Prompt (Fixes repeated messages and skips already answered questions)
        system_prompt = f"""You are a professional business representative from Ethnotec.
You are chatting with **{selected_client}**, who is a potential client.

### **Rules for Response Generation:**
- **DO NOT** introduce yourself again after the first message.
- **DO NOT** repeat the welcome message.
- **DO NOT** generate random client names. Always refer to `{selected_client}`.
- **ALWAYS** analyze past responses before asking a new question.
- If the client has **already answered a question in a previous message**, **DO NOT ask it again**.
- If the client answers **multiple questions in one message**, **SKIP those questions** and ask only the next relevant one.
- If the conversation reaches a natural conclusion, suggest scheduling a call.

### **Core Questions (To be asked one by one based on user responses):**
1. What industries do you target?
2. What kind of results are you expecting?
3. What challenges do you face in your campaigns?
4. What is your payout per sale?
5. What is your payout duration? Weekly or monthly?
6. Let's schedule a call. What time works for you?

### **Handling Client Responses:**
- If a client answers multiple questions at once, **do NOT repeat those questions**.
- Instead, acknowledge their response and move to the **next relevant question**.
- Example:
  - **Client:** "We target the healthcare industry, and we expect at least 500 conversions per month."
  - **Your Response:** "Got it! Healthcare is a great industry, and 500 conversions is a solid goal. What challenges do you usually face in your campaigns?"
  
- If the client asks an **unrelated question**, give a **short, polite answer** but quickly **redirect the conversation back to campaign outsourcing**.

Make sure the conversation feels **engaging, professional, and natural** while keeping the discussion **goal-oriented**.
"""

        # Generate AI-enhanced response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_prompt}]
            + chat_history
        )

        ai_reply = response.choices[0].message.content

        # Add AI response to conversation
        save_message(selected_client, "assistant", ai_reply)

    