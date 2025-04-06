from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import pandas as pd
import pickle
import requests
import datetime
import os
from supabase import create_client, Client
from nlp1 import load_data, train_nlp_model, recommend_scholarships

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(24)

# ======= Supabase Configuration =======
SUPABASE_URL = "https://ylgwhszyqazifnalrjos.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlsZ3doc3p5cWF6aWZuYWxyam9zIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE1NDMzMzIsImV4cCI6MjA1NzExOTMzMn0.pYSE1gvcJ-nkvhfZGhtByUdkmSGOGoM6vsr6dASjcao"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======= Scholarship Recommendation System =======
df = load_data("combined60.csv")
pipeline, tfidf_matrix, df = train_nlp_model(df)

# ======= Career Prediction System =======
with open('decision_tree_model.pkl', 'rb') as file:
    model = pickle.load(file)

df_career = pd.read_csv("dataset9000.csv")
X = df_career.drop(columns=['Role'])
X = pd.get_dummies(X, drop_first=True)
feature_names = X.columns

# ======= Groq API Configuration =======
GROQ_API_KEY = "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"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def fetch_career_description(career_role):
    """Fetch career description, beginner courses, and projects from Groq API."""
    prompt = f"""
    Provide a 2-sentence description of a {career_role}.
    Then, list 3 beginner-friendly courses with their platform names and links to the platform's homepage or search page (ensure the links are valid and up-to-date).
    Finally, list 3 beginner-friendly project ideas with their full valid URLs (ensure the URLs are valid and up-to-date).
    
    Format:
    Description: <2-sentence description>
    Courses: 
    1. <course1> - <platform> - <platform1 homepage or search page URL>
    2. <course2> - platform> - <platform1 homepage or search page URL>
    3. <course3> - <platform> - <platform1 homepage or search page URL>
    Projects: 
    1. <project1> - <platform> - <full URL starting with http:// or https:// (must be a valid link)>
    2. <project2> - <platform> - <full URL starting with http:// or https:// (must be a valid link)>
    3. <project3> - <platform> - <full URL starting with http:// or https:// (must be a valid link)>
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(GROQ_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error {response.status_code}: {response.json().get('error', {}).get('message', 'Unknown error')}"

# ======= Routes =======
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/career')
def career():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('career.html')

@app.route('/index')
def index():
    if not is_authenticated():
        return redirect(url_for('login_page'))
    return render_template('index.html')

# ======= Career Prediction Route =======
@app.route('/predict', methods=['POST'])
def predict():
    """Predicts the career role based on user input."""
    input_data = {key: [request.form[key]] for key in request.form.keys()}
    input_df = pd.DataFrame(input_data)

    # Encode categorical variables
    input_df_encoded = pd.get_dummies(input_df)
    input_df_encoded = input_df_encoded.reindex(columns=feature_names, fill_value=0)

    # Predict career role
    prediction = model.predict(input_df_encoded)
    predicted_role = prediction[0]

    # Fetch career details
    career_data = fetch_career_description(predicted_role)
    
    return render_template('result.html', prediction=predicted_role, career_info=career_data)


# ======= Scholarship Recommendation Route =======
@app.route('/recommend', methods=['POST'])
def recommend():
    """Recommends scholarships based on user input."""
    user_input = request.form.get('user_input')
    if not user_input:
        return jsonify({"error": "No input provided. Please enter a query."}), 400  

    recommendations = recommend_scholarships(user_input, pipeline, tfidf_matrix, df, top_n=100)
    
    return redirect(url_for('results', recommendations=json.dumps(recommendations)))



@app.route('/results')
def results():
    """Displays scholarship recommendation results."""
    recommendations_json = request.args.get('recommendations')
    if not recommendations_json:
        return "No recommendations found. Please try again.", 400  

    try:
        recommendations = json.loads(recommendations_json)
    except json.JSONDecodeError:
        return "Invalid recommendations data. Please try again.", 400  

    return render_template('results.html', recommendations=recommendations)



@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('loginpage.html')

# ======= Register API =======
@app.route('/register', methods=['POST'])
def register():
    data = request.json if request.content_type == "application/json" else request.form
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("fName", "")
    last_name = data.get("lName", "")

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"emailRedirectTo": "http://127.0.0.1:5000/confirm-email"}
        })
        user = response.user

        if user:
            supabase.table("users").insert({
                "id": user.id,
                "email": user.email,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
                "created_at": datetime.datetime.utcnow().isoformat()
            }).execute()

        return jsonify({"message": "User registered successfully! Please check your email for confirmation."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/confirm-email')
def confirm_email():
    access_token = request.args.get("access_token")

    if not access_token:
        return "Invalid confirmation link or token missing.", 400

    try:
        supabase.auth.verify_email(access_token)
        return redirect(url_for('login_page'))
    except Exception as e:
        return f"Error confirming email: {str(e)}", 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json if request.content_type == "application/json" else request.form
    email = data.get("email")
    password = data.get("password")

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session['access_token'] = response.session.access_token
        return jsonify({"message": "Login successful!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

# ======= Helper function =======
def is_authenticated():
    return 'access_token' in session

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
