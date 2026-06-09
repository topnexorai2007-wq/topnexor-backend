from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.genai as genai
import requests

# MongoDB
from pymongo import MongoClient

# Password Hash
from flask_bcrypt import Bcrypt

# Date Time
from datetime import datetime

app = Flask(__name__)
CORS(app)

bcrypt = Bcrypt(app)

# =========================
# HTML ROUTES
# =========================

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/chatpage")
def chatpage():
    return render_template("index.html")

@app.route("/register")
def registerpage():
    return render_template("register.html")

# =========================
# MONGODB CONNECTION (FIXED)
# =========================

client = MongoClient("mongodb+srv://topnexorai2007_db_user:oasNntd2W1ngd7eQ@cluster0.51ngzkn.mongodb.net/topnexor_ai?retryWrites=true&w=majority")

db = client["topnexor_ai"]

users = db["users"]
chat_history = db["chat_history"]
saved_notes = db["saved_notes"]
login_history = db["login_history"]

# =========================
# GEMINI AI
# =========================

gemini_client = genai.Client(
    api_key=os.getenv("AQ.Ab8RN6JNH5PldH7YlyuDwKpD-BHvYE83k_OA2QT_8y7zKpdgPg")
)

PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-2.5-flash-lite")

PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-2.5-flash-lite"

# =========================
# HUGGINGFACE
# =========================

HF_API_KEY = os.getenv("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")
HF_MODEL = "mistralai/Mistral-Medium-3.5-128B"
HF_MODEL = "mistralai/Mistral-Medium-3.5-128B"

def call_huggingface(prompt):

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data[0]["generated_text"]

    return "HuggingFace Error"

# =========================
# REGISTER
# =========================

@app.route("/register", methods=["POST"])
def register_user():

    data = request.get_json()

    name = data.get("name")
    phone = data.get("phone")
    password = data.get("password")
    language = data.get("language")

    existing_user = users.find_one({"phone": phone})

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Number already registered"
        })

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    users.insert_one({
        "name": name,
        "phone": phone,
        "password": hashed_password,
        "language": language
    })

    return jsonify({
        "success": True,
        "message": "Registration Successful"
    })

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    phone = data.get("phone")
    password = data.get("password")

    user = users.find_one({"phone": phone})

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        })

    if bcrypt.check_password_hash(user["password"], password):

        login_history.insert_one({
            "name": user["name"],
            "phone": phone,
            "time": str(datetime.now())
        })

        return jsonify({
            "success": True,
            "message": "Login Successful",
            "name": user["name"],
            "phone": user["phone"],
            "language": user["language"]
        })

    return jsonify({
        "success": False,
        "message": "Wrong Password"
    })

# =========================
# PROFILE
# =========================

@app.route("/profile", methods=["POST"])
def profile():

    data = request.get_json()

    phone = data.get("phone")

    user = users.find_one({"phone": phone})

    if user:
        return jsonify({
            "name": user["name"],
            "phone": user["phone"],
            "language": user["language"]
        })

    return jsonify({
        "message": "User not found"
    })

# =========================
# CHANGE PASSWORD
# =========================

@app.route("/change_password", methods=["POST"])
def change_password():

    data = request.get_json()

    phone = data.get("phone")
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    user = users.find_one({"phone": phone})

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        })

    if bcrypt.check_password_hash(user["password"], old_password):

        new_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")

        users.update_one(
            {"phone": phone},
            {"$set": {"password": new_hash}}
        )

        return jsonify({
            "success": True,
            "message": "Password Changed"
        })

    return jsonify({
        "success": False,
        "message": "Old Password Wrong"
    })

# =========================
# SAVE NOTES
# =========================

@app.route("/save_note", methods=["POST"])
def save_note():

    data = request.get_json()

    username = data.get("username")
    note = data.get("note")

    saved_notes.insert_one({
        "username": username,
        "note": note
    })

    return jsonify({
        "success": True,
        "message": "Note Saved"
    })

# =========================
# CHAT AI
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_msg = data.get("message", "")
    username = data.get("username", "guest")

    try:
        response = gemini_client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=user_msg
        )
        reply = response.text

    except:
        try:
            response = gemini_client.models.generate_content(
                model=FALLBACK_MODEL,
                contents=user_msg
            )
            reply = response.text

        except:
            reply = call_huggingface(user_msg)

    try:
        chat_history.insert_one({
            "username": username,
            "message": user_msg,
            "reply": reply,
            "time": str(datetime.now())
        })
    except Exception as e:
        print("MongoDB Error:", e)

    return jsonify({
        "reply": reply
    })
    return jsonify({
        "reply": reply
    })

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )