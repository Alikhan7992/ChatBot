from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from google import genai  
import mysql.connector
import re

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # Change this to a secure secret key

# Initialize Gemini API client
client = genai.Client(api_key="AIzaSyD0e8qphoqf77C-jeGBE3OezOvB9tkFG0I")  

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Munt@h@123",
    "database": "User"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def validate_phone(phone):
    pattern = r'^[0-9]{10,15}$'
    return re.match(pattern, phone)

def get_jamia_details(query, program=None, category=None, year=None):
    """Get university details with formatted responses"""
    query_lower = query.lower()
    
    # Admission process with context
    if "admission" in query_lower or "apply" in query_lower or "eligibility" in query_lower:
        response = "<strong>🎓 Admission Process Overview</strong>\n───────────────────────────────\n"
        
        if program:
            # Program-specific eligibility
            eligibility = {
                "B.Pharm": "<strong>10+2 with Physics, Chemistry, Biology/Mathematics (50% marks)</strong>",
                "MBA": "<strong>Bachelor's degree (50% marks) + Valid CAT/MAT score</strong>",
                "BA LLB": "<strong>10+2 (45% marks) + LSAT India score</strong>",
                "B.Tech": "<strong>10+2 with Physics, Chemistry, Mathematics (50% marks) + JEE Main score</strong>",
            }.get(program, "<strong>10+2 with minimum 50% marks</strong>")
            
            response += (
                f"<strong>For {program}:</strong>\n"
                f". <strong>Eligibility:</strong> {eligibility}\n"
                f". <strong>Entrance Exam:</strong> {'Required' if program in ['MBA', 'B.Tech', 'BA LLB'] else 'Not Required'}\n"
            )
        
        response += (
            "\n<strong>General Process:</strong>\n"
            ". <strong>Online Application</strong> (March-June)\n"
            ". <strong>Entrance Test</strong> (if applicable)\n"
            ". <strong>Interview/Counseling</strong>\n"
            ". <strong>Document Verification</strong>\n"
            ". <strong>Fee Payment</strong>\n\n"
            f"<strong>📅 Important Dates for {year if year else '2024'}:</strong>\n"
            ". <strong>Application Start:</strong> 1st March\n"
            ". <strong>Last Date:</strong> 30th June\n"
            ". <strong>Entrance Exam:</strong> 15th July\n"
            ". <strong>Results:</strong> 30th July"
        )
        return response
    
    # Prospectus response
    elif "prospectus" in query_lower:
        return """<strong>Jamia Hamdard University - Comprehensive Prospectus 2024-25</strong>
═══════════════════════════════════════════════════════════

<strong>🏛️ UNIVERSITY OVERVIEW</strong>
----------------------
. <strong>Established:</strong> 1989 
. <strong>Accreditations:</strong> NAAC 'A' Grade | UGC Recognized
. <strong>Campus:</strong> 50+ Acre Green Campus
. <strong>Faculty:</strong> 200+ Qualified Educators
. <strong>Location:</strong> New Delhi, India

<strong>🎓 ACADEMIC PROGRAMS</strong>
--------------------
<strong>UNDERGRADUATE (UG):</strong>
. B.Tech: CSE, ECE, Mechanical, Civil Engineering
. BBA: General, International Business
. B.Pharm: Pharmaceutical Sciences 
. B.Sc: Biotechnology, Chemistry, Physics

<strong>POSTGRADUATE (PG):</strong>
. M.Tech: Specializations Available
. MBA: Finance, Marketing, HR, International Business
. M.Pharm: Advanced Pharmaceutical Studies
. M.Sc: All Science Disciplines

<strong>DOCTORAL PROGRAMS:</strong>
. PhD: Engineering, Management, Pharmacy, Sciences

<strong>📝 ADMISSION PROCESS (2024-25)</strong>
-------------------------------
1. <strong>Online Application Portal Opens:</strong> 1 March 2024
2. <strong>Entrance Examination:</strong> Program-specific dates
3. <strong>Interview:</strong> For selected courses
4. <strong>Merit List Publication</strong>
5. <strong>Document Verification:</strong>
   . 10th/12th Marksheets
   . Transfer/Migration Certificate
   . Valid ID Proof
6. <strong>Fee Payment & Enrollment</strong>

<strong>💸 FEE STRUCTURE (Annual)</strong>
-------------------------
| Program       | Fees       |
|---------------|------------|
| B.Tech        | ₹1.25 L    |
| BBA           | ₹85,000    |
| MBA           | ₹1.5 L     |
| B.Pharm       | ₹1.1 L     |
| Hostel        | ₹60,000    |

<strong>🎖️ SCHOLARSHIPS & FINANCIAL AID</strong>
--------------------------------
. <strong>Merit Scholarships:</strong> Up to 100% Tuition Fee Waiver
. <strong>Special Categories:</strong>
  . SC/ST Candidates
  . Differently-Abled Students
  . Sports Achievers
  . National Rank Holders

<strong>🏫 CAMPUS FACILITIES</strong>
--------------------
. <strong>Digital Library:</strong> 100,000+ Volumes & E-Resources
. <strong>Advanced Labs:</strong> 15+ Specialized Laboratories
. <strong>Sports Complex:</strong> Indoor/Outdoor Facilities
. <strong>Residential Hostels:</strong> Separate Accommodation
. <strong>Smart Classrooms:</strong> Tech-Enabled Learning
. <strong>24/7 Wi-Fi:</strong> Campus-wide Connectivity

<strong>📈 PLACEMENT HIGHLIGHTS (2023)</strong>
-------------------------------
. <strong>Highest Package:</strong> ₹22 LPA
. <strong>Average Package:</strong> ₹6.5 LPA
. <strong>Top Recruiters:</strong>
  ┌──────────────┬──────────────┐
  │ Tech Giants  │ Pharma Majors│
  ├──────────────┼──────────────┤
  │ Amazon       │ Sun Pharma   │
  │ TCS          │ Cipla        │
  │ Infosys      │ Dr. Reddy's  │
  │ Wipro        │ Biocon       │
  └──────────────┴──────────────┘

<strong>📞 CONTACT INFORMATION</strong>
----------------------
☎️ <strong>Admissions Helpline:</strong> +91-11-26059688
📩 <strong>Email:</strong> admissions@jamiahamdard.edu
🌐 <strong>Website:</strong> www.jamiahamdard.edu
📑 <strong>Download Prospectus:</strong> https://ums.jamiahamdard.ac.in/Files/Prospectus.pdf
═══════════════════════════════════════════════════════════"""
    
    elif "course" in query_lower or "duration" in query_lower:
        return (
            "<strong>📚 Program Durations:</strong>\n"
            ". <strong>BBA:</strong> 3 years (6 semesters)\n"
            ". <strong>B.Tech:</strong> 4 years (8 semesters)\n"
            ". <strong>MBA:</strong> 2 years (4 semesters)\n"
            ". <strong>B.Pharm:</strong> 4 years (8 semesters)\n"
            ". <strong>BA LLB:</strong> 5 years (10 semesters)"
        )
    
    elif "scholarship" in query_lower or "financial aid" in query_lower:
        return (
            "<strong>🎖️ Scholarships Available:</strong>\n"
            ". <strong>Merit Scholarship</strong> (75%+ marks): Up to 50% fee waiver\n"
            ". <strong>Minority Scholarship:</strong> 25% for eligible students\n"
            ". <strong>SC/ST Scholarship:</strong> Full tuition fee waiver\n"
            ". <strong>Sports Scholarship:</strong> 25-100% waiver\n\n"
            "<strong>📝 Apply through:</strong> https://www.jamiahamdard.ac.in/scholarships-and-freeships?title=Scholarships%20&%20Freeships"
        )
    
    elif "placement" in query_lower or "career" in query_lower:
        return (
            "<strong>📈 Placement Highlights (2023):</strong>\n"
            ". <strong>Highest Package:</strong> ₹22 LPA (Amazon)\n"
            ". <strong>Average Package:</strong> ₹6.5 LPA\n"
            ". <strong>Top Recruiters:</strong>\n"
            "  . <strong>Tech:</strong> TCS, Infosys, Wipro\n"
            "  . <strong>Pharma:</strong> Sun Pharma, Cipla\n"
            "  . <strong>Law:</strong> Khaitan & Co, Trilegal"
        )
    
    elif "location" in query_lower or "map" in query_lower or "address" in query_lower:
        return "MAP_RESPONSE"
    
    elif "campus" in query_lower or "picture" in query_lower or "photo" in query_lower:
        return "CAMPUS_IMAGE"
    
    else:
        return None

# Routes
@app.route('/')
def home():
    """Home route - redirects to login"""
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handle user login"""
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
                session['is_guest'] = False
                return jsonify({"success": True, "redirect": url_for('chat_page')})
            else:
                return jsonify({"success": False, "error": "Invalid credentials"}), 401
        except mysql.connector.Error as e:
            return jsonify({"error": str(e)}), 500
    else:
        return render_template('login.html')

@app.route('/guest_login', methods=['POST'])
def guest_login():
    """Handle guest login"""
    session['username'] = 'Guest'
    session['is_guest'] = True
    return jsonify({"success": True, "redirect": url_for('chat_page')})

@app.route('/signup', methods=['POST'])
def signup():
    """Handle new user registration"""
    data = request.json if request.is_json else request.form
    username = data.get('username')
    Email = data.get('email')
    Phone_Number = data.get('Phone_Number')
    password = data.get('password')
    
    if not username or not password or not Email or not Phone_Number:
        return jsonify({"error": "All fields are required"}), 400
    
    # Validate email format
    if not validate_email(Email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    
    # Validate phone format
    if not validate_phone(Phone_Number):
        return jsonify({"error": "Please enter a valid Phone_Number (10-15 digits)"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = %s OR email = %s", (username, Email))
        
        if cursor.fetchone():
            return jsonify({"error": "Username or email already exists"}), 400
        
        cursor.execute("INSERT INTO users (user_name, email, Phone_Number, password) VALUES (%s, %s, %s, %s)", 
                      (username, Email, Phone_Number, password))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User registered successfully!"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.pop('username', None)
    session.pop('is_guest', None)
    return jsonify({"success": True})

@app.route('/chat', methods=['GET'])
def chat_page():
    """Render chat interface"""
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('chat.html', username=session['username'], is_guest=session.get('is_guest', False))

@app.route('/map')
def map_page():
    """Render map page"""
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    location = {
        'latitude': 28.6546,
        'longitude': 77.2935,
        'name': 'Jamia Hamdard',
        'address': 'Hamdard Nagar, New Delhi, India'
    }
    return render_template('map.html', location=location)

@app.route('/chat', methods=['POST'])
def chat_api():
    """Handle chat requests"""
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_input = request.json.get('message')
    
    # Process the question
    response = process_single_question(user_input)
    
    if response == "MAP_RESPONSE":
        return jsonify({
            "response": "Here's the location of Jamia Hamdard:",
            "map_redirect": url_for('map_page')
        })
    elif response == "CAMPUS_IMAGE":
        return jsonify({
            "response": "Jamia Hamdard Campus:",
            "image_url": "https://collegeadvisors.in/wp-content/uploads/2023/11/Jamia-Hamdard-University-campus.jpeg"
        })
    
    return jsonify({"response": response})

def process_single_question(question):
    """Process a single question and return response"""
    # First check our predefined responses
    details = get_jamia_details(question)
    if details:
        return details
    
    # For other questions, use Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=question
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return "I couldn't process your request. Please try again later."
    

if __name__ == '__main__':
    app.run(debug=True)
