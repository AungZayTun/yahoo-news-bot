import feedparser
import requests
import time
import os
import json

# Secrets ယူမယ်
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# BBC News URL
RSS_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"

# 🔥 AI Library မသုံးဘဲ Direct လှမ်းခေါ်မယ့် Function
def get_ai_summary(title, summary):
    # Gemini 1.5 Flash ကို တိုက်ရိုက်လှမ်းခေါ်မယ်
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    prompt = f"""
    Translate and summarize this news into BURMESE for a Telegram Channel:
    Title: {title}
    Summary: {summary}
    """
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"AI Error: {response.text}")
            return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
    print(f"Sending to Telegram ID: {CHANNEL_ID}...")
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Connection Error: {e}")

def process_news():
    print("Fetching BBC News... 🌍")
    
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("RSS Error: Could not fetch news.")
        return

    # ပထမဆုံး ၁ ပုဒ်ကို ယူပြီး ချက်ချင်းပို့မယ်
    entry = feed.entries[0]
    title = entry.title
    link = entry.link
    summary = entry.summary if 'summary' in entry else entry.title

    print(f"Testing with: {title}")
    
    # AI ကို လှမ်းခေါ်မယ်
    ai_result = get_ai_summary(title, summary)
    
    if ai_result:
        final_msg = f"{ai_result}\n\n🔗 {link}"
        send_to_telegram(final_msg)
        print("✅ Message Sent Success!")
    else:
        print("❌ AI Failed to generate summary.")

if __name__ == "__main__":
    process_news()
