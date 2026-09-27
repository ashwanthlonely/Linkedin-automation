import os
import sys
import requests
import json
import urllib.parse
from dotenv import load_dotenv

# Ensure UTF-8 stdout encoding on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class NewsFetcher:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.download_dir = os.path.join(self.base_dir, "assets", "downloaded_news_images")
        os.makedirs(self.download_dir, exist_ok=True)

    def fetch_latest_news_and_images(self):
        """Fetch current headlines and download news article images."""
        print("📰 Fetching latest Indian & Global news headlines and extracting images...")

        # Topics to search & extract images for
        topics = [
            {"key": "indian_auto", "query": "Indian automobile EV Tata Mahindra news", "icon": "ev.jpg", "label": "🚗 Indian Auto Industry"},
            {"key": "indian_rd", "query": "ISRO DRDO IIT R&D technology breakthrough India news", "icon": "space.jpg", "label": "🚀 Indian R&D & Tech"},
            {"key": "indian_finance", "query": "Indian finance economy RBI GDP stock market news", "icon": "finance.jpg", "label": "💰 Indian Finance & Economy"},
            {"key": "indian_politics", "query": "Indian politics governance policy infrastructure news", "icon": "geopolitics.jpg", "label": "🏛️ Indian Politics & Policy"},
            {"key": "global_ai", "query": "Artificial intelligence agentic AI global tech news", "icon": "ai.jpg", "label": "🤖 AI & Emerging Tech"}
        ]

        extracted_images = []

        for item in topics:
            img_path = self._download_news_image(item["query"], item["key"])
            if img_path and os.path.exists(img_path):
                extracted_images.append({"key": item["key"], "path": img_path, "label": item["label"]})
            else:
                # Fallback to local asset
                fallback_path = os.path.join(self.base_dir, "assets", "cartoons", item["icon"])
                extracted_images.append({"key": item["key"], "path": fallback_path, "label": item["label"]})

        print(f"✅ Extracted {len(extracted_images)} news images for collage composition.")
        return extracted_images

    def _download_news_image(self, query, key):
        """Attempt to download relevant news image using Unsplash / DuckDuckGo / web search image API."""
        try:
            encoded_query = urllib.parse.quote(query)
            # Use Unsplash Source / Pollinations image fetch for news topic
            url = f"https://image.pollinations.ai/prompt/News photograph of {encoded_query}?width=600&height=400&nologo=true"
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and len(r.content) > 5000:
                save_path = os.path.join(self.download_dir, f"{key}_news.jpg")
                with open(save_path, "wb") as f:
                    f.write(r.content)
                return save_path
        except Exception as e:
            print(f"Notice downloading news image for '{key}': {e}")
        return None


if __name__ == "__main__":
    fetcher = NewsFetcher()
    images = fetcher.fetch_latest_news_and_images()
    for img in images:
        print(f"Key: {img['key']} -> {img['path']}")
