import google.genai as genai

# Apna Gemini API key yahan daalo
GEMINI_API_KEY = "AIzaSyBTdcFq7tyRMHqpaE-LygaWUZn5AV4TMiE"

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "models/gemini-2.5-flash"

def test_gemini(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=[{"role": "user", "parts": [{"text": prompt}]}]
    )
    # New SDK me direct text property hoti hai
    return response.text

if __name__ == "__main__":
    reply = test_gemini("Hello Gemini, explain Newton's first law simply.")
    print("🤖 Gemini Reply:\n", reply)
