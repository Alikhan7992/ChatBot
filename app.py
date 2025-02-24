from flask import Flask, request, jsonify, render_template
from google import genai

app = Flask(__name__,template_folder="templates")

# Initialize the Gemini API client with your API key
client = genai.Client(api_key="AIzaSyBxaddgnVodOLryhNEAmLiq8U1Mj9xuai8")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    # Build an admissions-specific prompt for Jamia Hamdard University
    admission_context = (
        "You are a helpful admissions assistant for Jamia Hamdard University. "
        "Provide clear, concise, and accurate information regarding the admission process, "
        "eligibility criteria, important dates, fees, and other details related to Jamia Hamdard University admissions. "
        "User query: " + user_input
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=admission_context
        )
        answer = response.text
        return jsonify({"response": answer})
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return jsonify({"response": "An error occurred while processing your request."}), 500

if __name__ == '__main__':
    app.run(debug=True)
