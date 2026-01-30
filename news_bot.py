import feedparser
import google.generativeai as genai
import requests
import time
import os

# Secrets ယူမယ်
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

RSS_URL = "https://www.yahoo.com/news/rss/world"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
    print(f"Sending to Telegram ID: {CHANNEL_ID}...")
    try:
        response = requests.post(url, data=data)
        print(f"Telegram Response: {response.text}") 
    except Exception as e:
        print(f"Telegram Connection Error: {e}")

def process_news():
    print("Force Checking Yahoo News... 🔍")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("RSS Error")
        return

    # ပထမဆုံး ၁ ပုဒ်ကိုပဲ ယူပြီး ချက်ချင်းပို့မယ် (စမ်းသပ်ဖို့)
    entry = feed.entries[0]
    title = entry.title
    link = entry.link
    summary = entry.summary if 'summary' in entry else entry.title

    print(f"Testing with: {title}")

    prompt = f"""
    Summarize this news into BURMESE for a Telegram Channel (Breaking News style):
    Title: {title}
    Summary: {summary}
    """
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        
        final_msg = f"{result}\n\n🔗 {link}"
        send_to_telegram(final_msg)
        print("✅ Message Sent!")
            
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == "__main__":
    process_news()
