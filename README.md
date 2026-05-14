# 🤖 Ethnotec Business Chatbot

A professional business chatbot application built with **Streamlit** and **OpenAI API** to help manage conversations with potential clients about campaign outsourcing services.

## Features

- 💬 **AI-Powered Conversations** - Uses OpenAI API for intelligent responses
- 📋 **Client Management** - Add, delete, and rename clients
- 💾 **Chat History** - Stores all conversations in SQLite database
- 🎯 **Structured Workflow** - Guides conversations through key business questions
- 📋 **Response Copying** - Easy copy functionality for AI responses
- 🔄 **Context-Aware** - AI remembers past responses and avoids repetition

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/SyedAffan10/Ethnotec-Business-Chatbot.git
cd Ethnotec-Business-Chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage

- **Add Client** - Enter a client name in the sidebar and click "Add Client"
- **Select Client** - Choose from existing clients to view their chat history
- **Delete Client** - Click the delete button to remove a client and their conversation
- **Rename Client** - Update a client's name using the rename field
- **Chat** - Type messages to engage with the AI chatbot

## Technology Stack

- **Streamlit** - Web UI framework
- **OpenAI API** - AI chatbot engine
- **SQLite** - Database for clients and chat history
- **Python-dotenv** - Environment variable management

## Database

The app uses SQLite with two tables:
- `clients` - Stores client information
- `chat_history` - Stores all messages between users and the AI

---

**Purpose:** This chatbot is designed for Ethnotec to efficiently qualify and engage potential campaign management clients.
