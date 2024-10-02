from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import mysql.connector
import os


load_dotenv()

app = Flask(__name__)


openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)


db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
}

def get_db_connection():
    """Establish a new database connection."""
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.id, 
                   (SELECT user_message FROM messages WHERE conversation_id = c.id ORDER BY timestamp ASC LIMIT 1) AS first_message 
            FROM conversations c
        """)
        conversations = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(conversations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_conversation', methods=['POST'])
def create_conversation():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO conversations () VALUES ()")
        conversation_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'conversation_id': conversation_id})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_conversation/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_message, ai_response FROM messages WHERE conversation_id = %s", (conversation_id,))
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'messages': messages})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        conversation_id = data.get('conversation_id')

  
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
            temperature=1,
            max_tokens=2048,
        )
        ai_response = response.choices[0].message.content

  
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (conversation_id, user_message, ai_response) VALUES (%s, %s, %s)", 
                       (conversation_id, user_input, ai_response))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)