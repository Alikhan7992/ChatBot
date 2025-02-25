from flask import Flask, request, jsonify, render_template
from google import genai
import mysql.connector


app = Flask(__name__, template_folder="templates")


# Initialize Gemini API client (insert your API key)
client = genai.Client(api_key="AIzaSyBxaddgnVodOLryhNEAmLiq8U1Mj9xuai8")

def get_db_connection():
    return mysql.connector.connect(**db_config)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Munt@h@123",
    "database": "User"
}


# Hard-coded details from Jamia Hamdard (replace with real data or DB calls as needed)
def get_jamia_details(query):
    query_lower = query.lower()
    if "prospectus" in query_lower:
        return "Prospectus: Please download the prospectus from: https://jamiahamdard.edu/uploaded_files/prospectus.pdf"
    elif "course" in query_lower:
        # Example course details; update as per actual information
        return ("Course Details:\n"
                "- BBA: 3 years\n"
                "- B.Tech: 4 years\n"
                "- MBA: 2 years\n"
                "For more details, visit: https://jamiahamdard.edu/courses")
    elif "admission process" in query_lower:
        return ("Admission Process:\n"
                "1. Online Application\n"
                "2. Entrance Test\n"
                "3. Interview\n"
                "4. Merit List\n"
                "Visit https://jamiahamdard.edu/admissions for full details.")
    # Add more conditions as needed
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username exists
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"success": False, "error": "User already exists"}), 400

        # Insert new user
        query = "INSERT INTO users (user_name, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "User registered successfully!"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_name = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({"success": True, "token": "dummy-token", "user": user}), 200
        else:
            return jsonify({"success": False, "error": "Invalid username or password"}), 401
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, user_name FROM users")
        users = cursor.fetchall()
        conn.close()
        return jsonify(users), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    # Check for a valid token in the Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"response": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    if token != "dummy-token":
        return jsonify({"response": "Invalid token"}), 403

    # Extract the user's message
    user_input = request.json.get('message')
    
    # Check if the query matches predefined details from Jamia Hamdard
    details = get_jamia_details(user_input)
    if details:
        return jsonify({"response": details})
    
    # Otherwise, call Gemini API with a prompt for concise response
    admission_context = (
        "You are a helpful admissions assistant for Jamia Hamdard University. "
        "Answer ONLY in concise bullet points with no extra commentary, and keep your answer under 40 words. "
        "User query: " + user_input
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=admission_context
            # Optionally, if supported:
            # max_tokens=100,
            # temperature=0.5
        )
        full_answer = response.text.strip()
        
        # Optional post-processing: truncate if the response is too long
        max_length = 300  # character limit example
        if len(full_answer) > max_length:
            full_answer = full_answer[:max_length].rsplit('.', 1)[0] + "."
        
        return jsonify({"response": full_answer})
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return jsonify({"response": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
