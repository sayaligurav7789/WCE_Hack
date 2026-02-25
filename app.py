from flask import Flask, render_template, request, jsonify
from src.rag_pipeline import answer_question
import os

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Simple in-memory session history (for demo purposes)
# In a production app, this would use a database or session cookies
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
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
        
        # Save to history
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append(response_data)
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(chat_history)

@app.route('/clear', methods=['POST'])
def clear_history():
    global chat_history
    chat_history = []
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Bind to 0.0.0.0:5000 for Replit
    app.run(host='0.0.0.0', port=5000, debug=True)
