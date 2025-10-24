# MediPulse
**MediPulse** is an AI-powered healthcare dashboard that allows medical professionals to **search, analyze, and manage patient records intelligently**. Built with **Flask, Python, Elastic Cloud, and Gemini AI/LangChain**, it transforms healthcare data into actionable insights.

---

## 🌟 Features

* **Interactive Dashboard:** Visualize patient data with bar charts, pie charts, and cards for quick insights.
* **Patient Search:** Instantly filter patient records based on queries.
* **Detailed Patient Profiles:** View medical history, risk levels, and recommendations.
* **AI Assistance:** Gemini-powered AI chat provides real-time recommendations for patient care.
* **Secure Authentication:** Login and signup with session management and password validation.
* **Responsive Design:** Works seamlessly on desktop and mobile devices.

---

## 🛠 Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Database & Search:** Elastic Cloud (serverless)
* **AI Integration:** Gemini + LangChain
* **Authentication:** Session-based login/signup

---

## 🚀 Installation / Running Locally

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd MediPulse
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**

   ```bash
   python app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000`

---

## 📁 Folder Structure

```
MediPulse-dashboard/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── login.html
│   ├── signup.html
    ├── patients.html
│   ├── errors.html
    ├── layout.html
│   ├── ai_chat.html
│   └── search.html
├── static/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── logo.jpg
└── users.json
```

---

## 🔑 User Authentication

* **Signup:** Password must contain at least one letter, one number, one special character, and minimum 6 characters.
* **Login:** Session-based authentication to secure user data.

---

## 💡 Demo

* **Dashboard:** View charts and metrics.
* **Search:** Filter patient records dynamically.
* **Profile:** Access detailed patient info.
* **AI Recommendations:** Get real-time suggestions for care.

---

## 📌 Notes

* Make sure your **Elastic Cloud credentials** and **Gemini API keys** are correctly set in `.env`.
* All **static assets** like images, CSS, and JS are in the `static/` folder.

---

## 🔗 Links

* **Project Demo Video:** https://youtu.be/poMlmtD6KwU
* **Live Deployment:** https://medipulseai.up.railway.app/

---


