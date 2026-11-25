import os
import uuid
from flask import Flask, render_template, request, jsonify, session
from groq import Groq

app = Flask(__name__)
app.secret_key = "cosmic_aurora_secret_key"

# Hardcoded Groq API key as requested by the user
GROQ_API_KEY = ""

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Active in-memory storage for conversation histories: chat_id -> list of message dicts
# Structure: { "chat_id_1": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...] }
CONVERSATION_HISTORY = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/models", methods=["GET"])
def get_models():
    # Return available Groq models with friendly names
    models = [
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Default)", "desc": "Latest versatile high-quality 70B model"},
        {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant", "desc": "Ultra-fast model for responsive tasks"}
    ]
    return jsonify({"models": models})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message")
    chat_id = data.get("chat_id")
    model_id = data.get("model", "llama-3.3-70b-versatile")
    system_prompt = data.get("system_prompt", "You are an intelligent, helpful, and friendly AI Assistant.")

    if not message:
        return jsonify({"error": "Message is required"}), 400
    
    if not chat_id:
        chat_id = str(uuid.uuid4())

    # Retrieve or initialize in-memory conversation history
    if chat_id not in CONVERSATION_HISTORY:
        CONVERSATION_HISTORY[chat_id] = []
        
    history = CONVERSATION_HISTORY[chat_id]

    # If the history is empty, setup the system prompt
    if not history or history[0].get("role") != "system":
        history.insert(0, {"role": "system", "content": system_prompt})
    elif history[0].get("role") == "system" and history[0].get("content") != system_prompt:
        # Update system prompt if it has changed
        history[0]["content"] = system_prompt

    # Append user's new message
    history.append({"role": "user", "content": message})

    try:
        # Send full chat history payload to Groq
        chat_completion = client.chat.completions.create(
            messages=history,
            model=model_id,
            temperature=0.7,
            max_tokens=2048,
        )

        assistant_response = chat_completion.choices[0].message.content
        
        # Append assistant's response to the history payload to preserve context
        history.append({"role": "assistant", "content": assistant_response})
        
        return jsonify({
            "chat_id": chat_id,
            "response": assistant_response,
            "history_length": len(history)
        })

    except Exception as e:
        # Remove user's message if execution failed so it doesn't pollute history when retrying
        if history and history[-1]["role"] == "user":
            history.pop()
        return jsonify({"error": str(e)}), 500

@app.route("/api/clear", methods=["POST"])
def clear_history():
    data = request.json or {}
    chat_id = data.get("chat_id")
    if chat_id in CONVERSATION_HISTORY:
        del CONVERSATION_HISTORY[chat_id]
        return jsonify({"status": "success", "message": f"History for {chat_id} cleared"})
    return jsonify({"status": "not_found", "message": "No history found for this chat ID"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
