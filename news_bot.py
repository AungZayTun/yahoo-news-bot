import feedparser
import google.generativeai as genai
import requests
import time
import os
from datetime import datetime, timedelta, timezone
from dateutil import parser

# GitHub Secrets ကနေ Key တွေကို လှမ်းယူမယ် (လုံခြုံရေးအတွက်)
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

# Yahoo News RSS (World News)
RSS_URL = "https://www.yahoo.com/news/rss/world"

# AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

def is_recent_news(pub_date_str):
    # သတင်းက လွန်ခဲ့တဲ့ ၂၀ မိနစ်အတွင်း တက်ထားတာ ဟုတ်မဟုတ် စစ်မယ်
    try:
        pub_date = parser.parse(pub_date_str)
        now = datetime.now(timezone.utc)
        # Yahoo News Timezone နဲ့ ချိန်ညှိခြင်း
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=timezone.utc)
            
        diff = now - pub_date
        # ၁၅ မိနစ်တစ်ခါ run မှာမို့ ၂၅ မိနစ်အတွင်း သတင်းတွေကိုပဲ ယူမယ်
        return diff < timedelta(minutes=25)
    except:
        return False

def process_news():
    print("Checking Yahoo News on GitHub Server... ☁️")
    feed = feedparser.parse(RSS_URL)
    
    if not feed.entries:
        print("RSS Error")
        return

    news_found = False
    
    # နောက်ဆုံး ၅ ပုဒ်ကို စစ်မယ်
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link
        pub_date = entry.published
        summary = entry.summary if 'summary' in entry else entry.title

        # သတင်းအသစ် မဟုတ်ရင် ကျော်မယ်
        if not is_recent_news(pub_date):
            continue

        print(f"New News Found: {title}")
        news_found = True

        prompt = f"""
        Analyze this news for Myanmar audience:
        Title: {title}
        Summary: {summary}

        Step 1: Is this relevant/interesting to Myanmar people? (Tech, Politics, Economy, Viral, War). Answer YES or NO.
        
        Step 2: If YES, summarize it in BURMESE (Breaking News style with emojis).
        If NO, return "SKIP".
        """
        
        try:
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            if "SKIP" not in result:
                final_msg = f"{result}\n\n🔗 {link}"
                send_to_telegram(final_msg)
                print(f"✅ Sent: {title}")
                time.sleep(2)
            else:
                print(f"❌ Irrelevant: {title}")
                
        except Exception as e:
            print(f"AI Error: {e}")

    if not news_found:
        print("No new news in the last 20 mins.")

if __name__ == "__main__":
    process_news()
