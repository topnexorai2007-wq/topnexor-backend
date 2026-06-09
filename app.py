from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.genai as genai
import requests
import os

from pymongo import MongoClient
from flask_bcrypt import Bcrypt
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
# MONGODB CONNECTION
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
    api_key=os.getenv("GEMINI_API_KEY")
)

PRIMARY_MODEL = "models/gemini-2.5-flash"
FALLBACK_MODEL = "models/gemini-2.5-flash-lite"

# =========================
# HUGGINGFACE
# =========================

hf_token = os.getenv("HF_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

def call_huggingface(prompt):

    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

    headers = {
        "Authorization": f"Bearer {hf_token}"
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
# CHAT API
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

# =========================
# RUN SERVER (RENDER FIX)
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )