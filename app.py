from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from google import genai
import mysql.connector

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"   # session ke liye

# Initialize Gemini API client
client = genai.Client(api_key="AIzaSyD0e8qphoqf77C-jeGBE3OezOvB9tkFG0I")  

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Munt@h@123",
    "database": "User"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Hard-coded details (update as needed)
def get_jamia_details(query):
    query_lower = query.lower()
    if "prospectus" in query_lower:
        prospectus_text = (
            "Prospectus Content:\n"
            "------------------------------------------\n"
            "Welcome to the admissions prospectus for Jamia Hamdard University.\n"
            "Here you will find details about courses, admission process, eligibility criteria, "
            "and fee structure.\n"
            "For more detailed information, please contact our admissions office.\n"
            "------------------------------------------"
        )
        return prospectus_text
    elif "course" in query_lower:
        return (
            "Course Details:\n"
            "- BBA: 3 years\n"
            "- B.Tech: 4 years\n"
            "- MBA: 2 years\n"
            "For more details, contact our admissions office."
        )
    elif "admission process" in query_lower:
        return (
            "Admission Process:\n"
            "1. Online Application\n"
            "2. Entrance Test\n"
            "3. Interview\n"
            "4. Merit List\n"
            "Please visit our office for a detailed brochure."
        )
    else:
        return None

# Home route redirects to login page
@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE user_name = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['username'] = username
                return jsonify({"success": True, "redirect": url_for('chat_page')})
            else:
                return jsonify({"success": False, "error": "Invalid credentials"}), 401
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json if request.is_json else request.form
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        if cursor.fetchone():
            return jsonify({"error": "User already exists"}), 400
        query = "INSERT INTO users (user_name, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully!"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['GET'])
def chat_page():
    # Ensure user is logged in
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    # Simple token check can be replaced with better auth as needed.
    # Extract the user's message from JSON payload
    user_input = request.json.get('message')
    
    # Handle batch processing if input contains multiple questions
    if isinstance(user_input, list):
        responses = []
        for question in user_input:
            response = process_single_question(question)
            responses.append(response)
        return jsonify({"responses": responses})
    else:
        response = process_single_question(user_input)
        return jsonify({"response": response})

def process_single_question(question):
    details = get_jamia_details(question)
    if details:
        return details
    
    admission_context = (
        "You are a helpful admissions assistant for Jamia Hamdard University. "
        "Answer ONLY in concise bullet points with no extra commentary, and keep your answer under 40 words. "
        "User query: " + question
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=admission_context
        )
        full_answer = response.text.strip()
        max_length = 300
        if len(full_answer) > max_length:
            full_answer = full_answer[:max_length].rsplit('.', 1)[0] + "."
        return full_answer
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return "An error occurred while processing your request."

if __name__ == '__main__':
    app.run(debug=True)
