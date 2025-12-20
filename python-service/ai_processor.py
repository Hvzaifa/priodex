from dotenv import load_dotenv
load_dotenv()
import os
from app import articles_collection
import requests
from datetime import datetime
from app import summary_collection

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def summarize_with_groq(article, api_key):
    """
    Summarize a single article and store it in the summaries collection.
    """
    # 1️⃣ Extract content
    content = article.get("fullContentAvailable") or article.get("content")
    if not content:
        raise ValueError("Article has no content to summarize.")

    # 2️⃣ Metadata from article
    article_id = article["_id"]
    category = article.get("categories", "uncategorized")
    keywords = article.get("keywords", [])

    # 3️⃣ Groq API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"Summarize the following article in 2–3 concise sentences:\n\n{content[:5000]}"

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.3
    }

    response = requests.post(GROQ_URL, headers=headers, json=data).json()

    # 4️⃣ Error handling
    if "error" in response:
        raise Exception(f"Groq API Error: {response['error']['message']}")
    if "choices" not in response or not response["choices"]:
        raise Exception(f"Unexpected Groq response format: {response}")

    summary_text = response["choices"][0]["message"]["content"].strip()

    # 6️⃣ Build summary document
    summary_doc = {
        "articleId": article_id,
        "summary": summary_text,
        "generatedAt": datetime.utcnow()
    }

    # 7️⃣ Save to MongoDB
    inserted_id = summary_collection.insert_one(summary_doc).inserted_id

    # 8️⃣ Return summary info in desired format
    return {
        "status": "success",
        "summaryId": inserted_id,
    }

if __name__ == "__main__":
    article = articles_collection.find_one({})
    print(summarize_with_groq(article, os.getenv("GROQ_API_KEY")))