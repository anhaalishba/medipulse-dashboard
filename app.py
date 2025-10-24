import os
from flask import Flask, render_template, request, redirect, url_for, session
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import io
import base64
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

app = Flask(__name__, template_folder='layout')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# Gemini setup
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5
)

# for login
USERS_FILE = "users.json"
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
                return {}
            except json.JSONDecodeError:
                return {}
    return {}
# Save users to file
def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


# Elasticsearch setup
es = Elasticsearch(
    os.getenv("ELASTIC_URL"),
    api_key=os.getenv("ELASTIC_API_KEY")
)
index_name = os.getenv("ELASTIC_INDEX", "patientdata")


#   AI Search 
def search_patients(query=None, disease=None, status=None, date=None):
    """
    Smart search with Gemini + ElasticSearch.
    Gemini converts user query (natural language) into key-value filters.
    Python safely parses them (no JSON errors).
    """
 
    instruction = (
        "You are a medical query interpreter. "
        "Read the user's query and extract filters as key-value pairs. "
        "Use keys like: disease, gender, min_age, max_age, sugar_condition ('normal' or 'abnormal'), "
        "bp_condition ('normal' or 'high'), heart_rate_condition ('normal' or 'high'), date_range.\n\n"
        "Example:\n"
        "Query: show diabetic female above age 40\n"
        "Output:\n"
        "disease: diabetes\n"
        "gender: female\n"
        "min_age: 40"
    )

    messages_json = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": f"Query: {query}"}
    ]

    try:
        ai_response = model.invoke(messages_json)
        ai_text = ai_response.content.strip()
        print("Gemini raw response:\n", ai_text)
    except Exception as e:
        ai_text = ""
        print("Gemini Error:", e)

    filters = {}
    for line in ai_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            filters[key.strip().lower()] = value.strip().lower()

    text = ai_text.lower()
    if "diabet" in text:
        filters.setdefault("disease", "diabetes")
    if "female" in text:
        filters.setdefault("gender", "female")
    if "male" in text:
        filters.setdefault("gender", "male")
    if "above 40" in text or "older than 40" in text:
        filters.setdefault("min_age", 40)

    print("Final parsed filters:", filters)

    must_clauses = []

    def match_or_term(field, value):
        return {"bool": {"should": [
            {"match": {field: value}},
                {"term": {field: value.lower()}},
        {"term": {field: value.capitalize()}}
        ]}}

    if filters.get("disease"):
        must_clauses.append(match_or_term("disease", filters["disease"]))
    if filters.get("gender"):
        must_clauses.append(match_or_term("gender", filters["gender"]))
    if filters.get("sugar_condition") == "abnormal":
        must_clauses.append(match_or_term("status", "Abnormal Sugar"))
    if filters.get("bp_condition") == "high":
        must_clauses.append(match_or_term("status", "Abnormal BP"))
    if filters.get("min_age"):
        must_clauses.append({"range": {"age": {"gte": int(filters["min_age"])}}})
    if filters.get("max_age"):
        must_clauses.append({"range": {"age": {"lte": int(filters["max_age"])}}})

    search_body = {"query": {"bool": {"must": must_clauses}}} if must_clauses else {"query": {"match_all": {}}}

    try:
        resp = es.search(index=index_name, body=search_body)
        records = [hit["_source"] for hit in resp['hits']['hits']]
    except Exception as e:
        records = []
        print("ElasticSearch Error:", e)

    return records  


@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        users = load_users()

        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            message = "❌ Invalid email or password!"
            return render_template('login.html', message=message)

    return render_template('login.html', message=message)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = "" 

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        users = load_users()  
        if email in users:
            message = "⚠️ User already exists! Please login."
            return render_template('signup.html', message=message)

        if len(password) < 6:
            message = "⚠️ Password must be at least 6 characters long."
        elif not re.search(r"[A-Za-z]", password):
            message = "⚠️ Password must contain at least one letter."
        elif not re.search(r"\d", password):
            message = "⚠️ Password must contain at least one digit."
        elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            message = "⚠️ Password must contain at least one special character."
        else:
            users[email] = {"password": password}
            save_users(users)
            message = "✅ Signup successful! You can now login."
            return render_template('login.html', message=message)

        return render_template('signup.html', message=message)

    return render_template('signup.html', message=message)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user'] 

    all_patients = search_patients()  
    total_patients = len(all_patients)

    critical_cases_list = [p for p in all_patients if p.get('status') in ['Abnormal Sugar', 'Abnormal BP']]
    critical_cases_count = len(critical_cases_list)

    # New records (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    new_records_list = []
    for p in all_patients:
        last_report = p.get('last_report')
        if last_report:
            try:
                report_date = datetime.strptime(last_report, "%Y-%m-%d")
                if report_date >= week_ago:
                    new_records_list.append(p)
            except:
                pass
    new_records_count = len(new_records_list)

    
    

    # --- Chart Data from ElasticSearch ---
    gender_counts = {}
    condition_counts = {}
    for r in all_patients:
        gender = r.get('gender', 'Unknown')
        disease_name = r.get('disease', 'Unknown')
        gender_counts[gender] = gender_counts.get(gender, 0) + 1
        condition_counts[disease_name] = condition_counts.get(disease_name, 0) + 1

    # --- Gender Pie Chart ---
    fig1, ax1 = plt.subplots()
    ax1.pie(gender_counts.values(), labels=gender_counts.keys(), autopct='%1.1f%%', colors=['#36A2EB', '#FF6384'])
    ax1.set_title("Gender Distribution")
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format='png', bbox_inches='tight')
    buf1.seek(0)
    gender_chart = base64.b64encode(buf1.getvalue()).decode('utf-8')
    plt.close(fig1)

    # --- Disease Bar Chart ---
    fig2, ax2 = plt.subplots()
    ax2.bar(condition_counts.keys(), condition_counts.values(), color='#4BC0C0')
    ax2.set_title("Disease Frequency")
    ax2.set_ylabel("Number of Patients")
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format='png', bbox_inches='tight')
    buf2.seek(0)
    condition_chart = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close(fig2)
    
    
    return render_template(
        'dashboard.html',
        username=username,
        total_patients=total_patients,
        critical_cases=critical_cases_count,
        new_records=new_records_count,
        gender_chart=gender_chart,
        condition_chart=condition_chart,
        all_patients=all_patients,
        critical_cases_list=critical_cases_list,
        new_records_list=new_records_list,
        hide_footer=True
    )

@app.route('/search', methods=['POST'])
def search_page():
    query = request.form.get('query')
    disease = request.form.get('disease')
    status = request.form.get('status')
    date = request.form.get('last_report')

    results = search_patients(query, disease, status, date)

    return render_template('search.html', user_query=query, results=results)

@app.route('/patients')
def patients():
    patient_list = search_patients()
    return render_template('patients.html', patients=patient_list)

@app.route('/ai-chat', methods=['GET', 'POST'])
def ai_chat():
    messages = [
        {"role": "system", "content": "You are a smart AI assistant for patient health recommendations. Respond concisely and professionally."}
    ]
    response_text = ""
    
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        messages.append({"role": "user", "content": user_input})
        
        try:
            result = model.invoke(messages)
            response_text = result.content
            messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            response_text = f"AI Error: {e}"
            messages.append({"role": "assistant", "content": response_text})
    
    return render_template("ai_chat.html", messages=messages, response_text=response_text, hide_footer=True)



@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    users = load_users()  

    user_data = users.get(email, {})

    user = {
        'fullname': user_data.get('fullname', email.split('@')[0].title()),  
        'email': email
    }

    return render_template('profile.html', user=user)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port, debug=True)

