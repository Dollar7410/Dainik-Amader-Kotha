import os
import json
import urllib.request
import xml.etree.ElementTree as ET

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
RSS_URL = "https://news.google.com/rss?hl=bn&gl=BD&ceid=BD:bn"

def get_latest_rss_headlines():
    try:
        req = urllib.request.Request(RSS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        xml_data = urllib.request.urlopen(req).read()
        root = ET.fromstring(xml_data)
        items = []
        for item in root.findall('.//item')[:6]:
            title = item.find('title').text if item.find('title') is not None else ""
            items.append({"raw_title": title})
        return items
    except Exception as e:
        print(f"RSS Error: {e}")
        return []

def rewrite_with_gemini(raw_news):
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is missing!")
        return None
        
    prompt = f"""
    You are Chief Editor of 'দৈনিক আমাদের কথা'. Rewrite these raw news items into 6 engaging newspaper articles in Bengali.
    Raw items: {json.dumps(raw_news, ensure_ascii=False)}
    Respond ONLY with a valid JSON array format:
    [
      {{
        "id": 1,
        "title": "শিরোনাম",
        "category": "জাতীয়",
        "time": "১৫ মিনিট আগে",
        "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80",
        "summary": "সারসংক্ষেপ...",
        "views": 120
      }}
    ]
    No markdown backticks like ```json in output.
    """
    
    # Gemini 1.5 Flash API Endpoint
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=){GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        text = result['candidates'][0]['content']['parts'][0]['text'].strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def main():
    raw = get_latest_rss_headlines()
    print(f"Fetched {len(raw)} RSS items.")
    if raw:
        processed = rewrite_with_gemini(raw)
        if processed:
            with open('news.json', 'w', encoding='utf-8') as f:
                json.dump(processed, f, ensure_ascii=False, indent=2)
            print("Successfully created news.json!")
        else:
            print("Failed to process news with Gemini.")

if __name__ == "__main__":
    main()
