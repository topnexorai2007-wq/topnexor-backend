import requests

# Apna Gemini API key yahan daalo
GEMINI_API_KEY = "AIzaSyBTdcFq7tyRMHqpaE-LygaWUZn5AV4TMiE"

# Endpoint for listing models
url = f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_API_KEY}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("✅ Available Gemini Models:\n")
    for m in data.get("models", []):
        print("-", m["name"])
else:
    print("⚠️ Error:", response.text)
