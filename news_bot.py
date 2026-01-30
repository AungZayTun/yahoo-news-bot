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

# 🛑 Yahoo က Block တာ ရှောင်ဖို့ "လူယောင်ဆောင်မယ့်" ခေါင်းစဉ်
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

def process_news():
    print("Force Checking Yahoo News (Stealth Mode)... 🕵️")
    
    try:
        # requests နဲ့ အရင်လှမ်းယူမယ် (Block မခံရအောင်)
        response = requests.get(RSS_URL, headers=HEADERS, timeout=15)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"Connection Error: {e}")
        return
    
    if not feed.entries:
        print("RSS Error: Still blocked or no internet on server.")
        return

    # ပထမဆုံး ၁ ပုဒ်ကိုပဲ ယူပြီး ချက်ချင်းပို့မယ်
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
        print("✅ Message Sent!")
            
    except Exception as e:
        print(f"AI Error: {e}")

if __name__ == "__main__":
    process_news()
