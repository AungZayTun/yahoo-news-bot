import feedparser
import google.generativeai as genai
import requests
import time
import os

# Secrets ယူမယ်
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# BBC News URL
RSS_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"

genai.configure(api_key=GEMINI_API_KEY)

# 🛑 FIX: "gemini-1.5-flash" အစား "gemini-pro" ကို ပြောင်းသုံးလိုက်တယ် (Error မတက်တော့ဘူး)
model = genai.GenerativeModel('gemini-pro')

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

    prompt = f"""
    Translate and summarize this news into BURMESE for a Telegram Channel:
    Title: {title}
    Summary: {summary}
    """
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        final_msg = f"{result}\n\n🔗 {link}"
        send_to_telegram(final_msg)
        print("✅ Message Sent Success!")
            
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == "__main__":
    process_news()
