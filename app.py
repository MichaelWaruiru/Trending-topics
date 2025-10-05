from flask import Flask, render_template, jsonify
from bs4 import BeautifulSoup
import requests
import json
import subprocess
import re

app = Flask(__name__)

def fetch_google_trends(region="US", limit=10):
    """Scrape trending topics directly from Google Trends"""
    url = f"https://trends.google.com/trending?geo={region.upper()}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch trends, status={response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    topics = []

    # Google changes layout often; we handle multiple possibilities
    for tag in soup.find_all(["span", "div"], string=True):
        text = tag.get_text(strip=True)
        if len(text.split()) <= 10 and re.match(r"^[A-Za-z0-9\s\-&']+$", text):
            topics.append(text)

    topics = list(dict.fromkeys(topics))  # remove duplicates
    print("Trending topics:", topics)
    return topics[:limit]


def paraphrase_text(text: str) -> str:
    """Call your local DeepSeek model to paraphrase"""
    try:
        # Example: Replace this command with your actual local inference call
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b", f"Paraphrase this: {text}"],
            capture_output=True, text=True, timeout=30
        )
        paraphrased = result.stdout.strip()
        # Fallback if empty
        if not paraphrased:
            paraphrased = text
        return paraphrased
    except Exception as e:
        return f"[Error paraphrasing: {e}]"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/trends")
def get_trends():
    try:
        topics = fetch_google_trends(region="US", limit=10)
        paraphrased = []
        for t in topics:
            paraphrased.append({
                "original": t,
                "paraphrased": paraphrase_text(t)
            })
        return jsonify(paraphrased)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
