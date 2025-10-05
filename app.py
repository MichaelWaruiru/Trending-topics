from flask import Flask, jsonify, render_template
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import subprocess

app = Flask(__name__)

def fetch_google_trends(region="US", limit=10):
    """Scrape realtime Google trending topics using Playwright with Chromium."""
    region = region.upper()
    url = f"https://trends.google.com/trending?geo={region}"
    topics = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # ✅ use Chromium/Chrome
        page = browser.new_page()
        page.goto(url, timeout=20000)
        page.wait_for_timeout(5000)  # wait for JS-rendered data

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        # Extract topic text; filter out UI/irrelevant elements
        for tag in soup.find_all(["span", "div"], string=True):
            text = tag.get_text(strip=True)
            if (
                text
                and len(text.split()) < 10
                and not any(x.lower() in text.lower() for x in [
                    "home", "explore", "sign", "feedback", "category", "search", "trend"
                ])
            ):
                topics.append(text)

        browser.close()

    # Remove duplicates and limit results
    topics = list(dict.fromkeys(topics))
    return topics[:limit]


def paraphrase_text(text: str) -> str:
    """Call local Ollama model to paraphrase."""
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b", f"Paraphrase this phrase: {text}"],
            capture_output=True, text=True, timeout=30
        )
        paraphrased = result.stdout.strip()
        return paraphrased if paraphrased else text
    except Exception as e:
        return f"[Error paraphrasing: {e}]"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/trends")
def get_trends():
    try:
        topics = fetch_google_trends(region="US", limit=10)
        paraphrased = [{"original": t, "paraphrased": paraphrase_text(t)} for t in topics]
        return jsonify(paraphrased)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
