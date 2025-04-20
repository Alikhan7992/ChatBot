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
        return """Jamia Hamdard University - Comprehensive Prospectus 2024-25
═══════════════════════════════════════════════════════════

🏛️ UNIVERSITY OVERVIEW
----------------------
- Established: 1989 
- Accreditations: NAAC 'A' Grade | UGC Recognized
- Campus: 50+ Acre Green Campus
- Faculty: 200+ Qualified Educators
- Location: New Delhi, India

🎓 ACADEMIC PROGRAMS
--------------------
UNDERGRADUATE (UG):
- B.Tech: CSE, ECE, Mechanical, Civil Engineering
- BBA: General, International Business
- B.Pharm: Pharmaceutical Sciences 
- B.Sc: Biotechnology, Chemistry, Physics

POSTGRADUATE (PG):
- M.Tech: Specializations Available
- MBA: Finance, Marketing, HR, International Business
- M.Pharm: Advanced Pharmaceutical Studies
- M.Sc: All Science Disciplines

DOCTORAL PROGRAMS:
- PhD: Engineering, Management, Pharmacy, Sciences

📝 ADMISSION PROCESS (2024-25)
-------------------------------
1. Online Application Portal Opens: 1 March 2024
2. Entrance Examination: Program-specific dates
3. Interview: For selected courses
4. Merit List Publication
5. Document Verification:
   - 10th/12th Marksheets
   - Transfer/Migration Certificate
   - Valid ID Proof
6. Fee Payment & Enrollment

💸 FEE STRUCTURE (Annual)
-------------------------
| Program       | Fees       |
|---------------|------------|
| B.Tech        | ₹1.25 L    |
| BBA           | ₹85,000    |
| MBA           | ₹1.5 L     |
| B.Pharm       | ₹1.1 L     |
| Hostel        | ₹60,000    |

🎖️ SCHOLARSHIPS & FINANCIAL AID
--------------------------------
- Merit Scholarships: Up to 100% Tuition Fee Waiver
- Special Categories:
  - SC/ST Candidates
  - Differently-Abled Students
  - Sports Achievers
  - National Rank Holders

🏫 CAMPUS FACILITIES
--------------------
- Digital Library: 100,000+ Volumes & E-Resources
- Advanced Labs: 15+ Specialized Laboratories
- Sports Complex: Indoor/Outdoor Facilities
- Residential Hostels: Separate Accommodation
- Smart Classrooms: Tech-Enabled Learning
- 24/7 Wi-Fi: Campus-wide Connectivity

📈 PLACEMENT HIGHLIGHTS (2023)
-------------------------------
- Highest Package: ₹22 LPA
- Average Package: ₹6.5 LPA
- Top Recruiters:
  ┌──────────────┬──────────────┐
  │ Tech Giants  │ Pharma Majors│
  ├──────────────┼──────────────┤
  │ Amazon       │ Sun Pharma   │
  │ TCS          │ Cipla        │
  │ Infosys      │ Dr. Reddy's  │
  │ Wipro        │ Biocon       │
  └──────────────┴──────────────┘

📞 CONTACT INFORMATION
----------------------
☎️ Admissions Helpline: +91-11-26059688
📩 Email: admissions@jamiahamdard.edu
🌐 Website: www.jamiahamdard.edu
📑 Download Prospectus: https://ums.jamiahamdard.ac.in/Files/Prospectus.pdf
═══════════════════════════════════════════════════════════"""

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
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    user_input = request.json.get('message')
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
        "Answer ONLY in concise bullet points with no extra commentary, and keep your answer under 200 words. "
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
