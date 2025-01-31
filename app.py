from flask import Flask, request, jsonify
import requests
import feedparser
import re
import wikipediaapi
from transformers import pipeline

ITMO_NEWS_RSS = "https://news.itmo.ru/ru/rss/"

app = Flask(__name__)

model = pipeline("text2text-generation", model="google/flan-t5-large")

wiki_wiki = wikipediaapi.Wikipedia(
    language='ru',
    user_agent='ITMO_Bot/1.0 (https://itmo.ru; your-email@example.com)'
)


def generate_response(query):
    try:
        prompt = f"""Вопрос: {query}
Ответь только номером правильного варианта (1-10). Если вопрос не требует выбора, напиши 'null'."""

        result = model(prompt, max_length=50, num_return_sequences=1)
        return result[0].get("generated_text", "").strip()
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_wiki(query):
    try:
        page = wiki_wiki.page(query)
        return page.summary[:500] if page.exists() else None
    except Exception as e:
        print(f"Wiki error: {e}")
        return None


def fetch_news():
    try:
        feed = feedparser.parse(ITMO_NEWS_RSS)
        return [entry.link for entry in feed.entries[:3]]
    except Exception as e:
        print(f"News error: {e}")
        return []


def extract_answer(text):
    match = re.search(r'(?i)\b(null|10|\d)\b', text)
    if match:
        value = match.group(0)
        return None if value.lower() == "null" else int(value)
    return None


@app.route('/')
def home():
    return "ITMO Bot API. Send POST requests to /api/request."


@app.route('/api/request', methods=['POST'])
def process_request():
    data = request.get_json()
    if not data or "query" not in data or "id" not in data:
        return jsonify({"error": "Invalid request"}), 400

    query, req_id = data["query"], data["id"]
    llm_answer = generate_response(query)
    answer_number = extract_answer(llm_answer) if llm_answer else None

    is_multiple_choice = re.search(r'\n1\.', query) is not None

    sources = []
    if is_multiple_choice:
        wiki_summary = fetch_wiki(query)
        if wiki_summary:
            sources.append({"type": "wikipedia", "content": wiki_summary})
    else:
        news_links = fetch_news()
        sources.extend([{"type": "itmo_news", "link": link} for link in news_links])

    reasoning = "No response" if not llm_answer else f"Model response: {llm_answer}"
    response = {
        "id": req_id,
        "answer": answer_number if is_multiple_choice else None,
        "reasoning": reasoning,
        "sources": sources[:3]
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
