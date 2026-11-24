import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "aiverse_secret_123")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging in entry.get("messaging", []):
                sender_id = messaging["sender"]["id"]
                if "message" in messaging and "text" in messaging["message"]:
                    user_text = messaging["message"]["text"]
                    reply_text = ask_gemini(user_text)
                    send_message(sender_id, reply_text)
    return "OK", 200

def ask_gemini(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception:
        return "ခဏစောင့်ပြီး ပြန်ပို့ပေးပါ။"

def send_message(recipient_id, text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text[:2000]}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
