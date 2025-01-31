from flask import Flask, request, jsonify
import requests
import feedparser
import re
import wikipediaapi  # Для работы с Википедией
from transformers import pipeline  # Для работы с локальной моделью

ITMO_NEWS_RSS = "https://news.itmo.ru/ru/rss/"

app = Flask(__name__)

model = pipeline("text2text-generation", model="google/flan-t5-large")  # Используем модель FLAN-T5

wiki_wiki = wikipediaapi.Wikipedia(
    language='ru',  # Язык Википедии
    user_agent='ITMO_Bot/1.0 (https://itmo.ru; your-email@example.com)'  # Указываем User-Agent
)


def get_llm_answer(query):
    """Генерация ответа с использованием локальной модели."""
    try:
        prompt = f"""Вопрос: {query}
Ответь только номером правильного варианта (1-10). Если вопрос не требует выбора, напиши 'null'."""

        result = model(prompt, max_length=50, num_return_sequences=1)
        generated_text = result[0].get("generated_text", "").strip()
        return generated_text
    except Exception as e:
        print(f"Ошибка генерации текста: {e}")
        return None


def wikipedia_search(query):
    """Поиск информации в Википедии."""
    try:
        page = wiki_wiki.page(query)
        if page.exists():
            return page.summary[:500]  # Возвращаем первые 500 символов статьи
        else:
            return None
    except Exception as e:
        print(f"Ошибка поиска в Википедии: {e}")
        return None


def get_itmo_news():
    """Получение последних новостей ИТМО."""
    try:
        feed = feedparser.parse(ITMO_NEWS_RSS)
        return [entry.link for entry in feed.entries[:3]]  # Возвращаем 3 последние новости
    except Exception as e:
        print(f"Ошибка новостей: {e}")
        return []


def parse_answer(answer_text):
    """Извлечение номера ответа из текста."""
    match = re.search(r'(?i)\b(null|10|\d)\b', answer_text)
    if match:
        value = match.group(0)
        if value.lower() == "null":
            return None
        return int(value)
    return None


@app.route('/')
def index():
    return "Welcome to the ITMO bot API! Please send a POST request to /api/request."


@app.route('/api/request', methods=['POST'])
def handle_request():
    data = request.get_json()
    if not data or "query" not in data or "id" not in data:
        return jsonify({"error": "Invalid request"}), 400

    query = data["query"]
    req_id = data["id"]

    # Получение ответа от модели
    llm_answer = get_llm_answer(query)
    answer_number = parse_answer(llm_answer) if llm_answer else None

    is_multiple_choice = re.search(r'\n1\.', query) is not None

    sources = []
    if is_multiple_choice:
        # Для вопросов с выбором используем Википедию
        wiki_summary = wikipedia_search(query)
        if wiki_summary:
            sources.append({"type": "wikipedia", "content": wiki_summary})
    else:
        # Для остальных вопросов используем новости ИТМО
        news_links = get_itmo_news()
        sources.extend([{"type": "itmo_news", "link": link} for link in news_links])

    # Формирование ответа
    reasoning_message = "Не удалось получить ответ" if not llm_answer else f"Ответ сгенерирован моделью. {llm_answer}"
    response = {
        "id": req_id,
        "answer": answer_number if is_multiple_choice else None,
        "reasoning": reasoning_message,
        "sources": sources[:3]  # Не более 3 источников
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)