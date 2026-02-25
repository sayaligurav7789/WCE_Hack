from flask import Flask, render_template, request, jsonify, session
from src.rag_pipeline import answer_question
import os
import uuid
from datetime import timedelta

app = Flask(
    __name__,
    template_folder='src/templates',
    static_folder='src/static'
)

# Set a secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.permanent_session_lifetime = timedelta(days=7)

# In-memory storage for chats
chat_storage = {}

@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    chat_id = data.get('chat_id', 'default')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    session_id = session.get('session_id', 'anonymous')
    
    try:
        answer, context, sections, pages = answer_question(user_message)
        
        response_data = {
            "role": "assistant",
            "content": answer,
            "references": {
                "sections": sections,
                "pages": pages
            }
        }
        
        # Store chat
        if session_id not in chat_storage:
            chat_storage[session_id] = {}
        
        if chat_id not in chat_storage[session_id]:
            chat_storage[session_id][chat_id] = {
                "messages": [],
                "preview": user_message[:50] + "..." if len(user_message) > 50 else user_message
            }
        
        # Add messages
        chat_storage[session_id][chat_id]["messages"].extend([
            {"role": "user", "content": user_message},
            response_data
        ])
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@app.route('/history', methods=['GET'])
def get_history():
    session_id = session.get('session_id', 'anonymous')
    return jsonify(chat_storage.get(session_id, {}))

@app.route('/chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    session_id = session.get('session_id', 'anonymous')
    if session_id in chat_storage and chat_id in chat_storage[session_id]:
        del chat_storage[session_id][chat_id]
        return jsonify({"status": "success"})
    return jsonify({"error": "Chat not found"}), 404

@app.route('/clear', methods=['POST'])
def clear_history():
    session_id = session.get('session_id', 'anonymous')
    if session_id in chat_storage:
        chat_storage[session_id] = {}
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)