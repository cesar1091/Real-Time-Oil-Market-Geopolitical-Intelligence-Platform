import spacy
import logging
from datetime import datetime
from collections import Counter

from database.db import *

logging.basicConfig(level=logging.INFO)


def _load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError as e:
        logging.warning(
            "SpaCy model en_core_web_sm not found. Using spacy.blank('en') fallback: %s",
            e,
        )
        return spacy.blank("en")


NLP = _load_nlp_model()


def _extract_keywords(text: str):
    doc = NLP(text)

    # Use POS tagging if available
    keywords = [
        token.text.lower()
        for token in doc
        if token.pos_ in ("NOUN", "PROPN")
        and not token.is_stop
        and token.is_alpha
    ]

    if keywords:
        return keywords

    # Fallback when using spacy.blank("en")
    return [
        token.text.lower()
        for token in doc
        if token.is_alpha
        and len(token.text) >= 3
        and not token.is_stop
    ]


def fetch_news_analytics() -> dict:
    try:
        db = getDatabase()
        news_table = getNewsTable(db)
        news_data = news_table.all()

        daily_keyword_counts = {}

        for entry in news_data:
            title = entry.get("title", "")
            published = entry.get("published", "")

            try:
                published_date = datetime.strptime(
                    published,
                    "%a, %d %b %Y %H:%M:%S GMT"
                )
                published_day = published_date.strftime("%d-%m-%Y")
            except Exception:
                published_day = "unknown"

            keywords = _extract_keywords(title)

            daily_keyword_counts.setdefault(
                published_day,
                Counter()
            ).update(keywords)

        top_keywords_by_day = {
            day: counts.most_common(20)
            for day, counts in daily_keyword_counts.items()
        }

        return {"top_keywords_by_day": top_keywords_by_day}

    except Exception as e:
        logging.exception("Error fetching news analytics")
        return {"top_keywords_by_day": {}}


def save_top_k_analysis_to_db(top_k_analysis: dict, top_k_table):
    top_k_table.truncate()  # optional: avoid duplicates

    for day, keywords in top_k_analysis.get(
        "top_keywords_by_day",
        {}
    ).items():
        top_k_table.insert(
            {
                "date": day,
                "top_keywords": keywords,
            }
        )

    logging.info(
        "Inserted %d top-k analysis records.",
        len(top_k_analysis.get("top_keywords_by_day", {}))
    )


if __name__ == "__main__":
    db = getDatabase()
    top_k_table = getTopKTable(db)

    top_k_analysis = fetch_news_analytics()

    if top_k_analysis.get("top_keywords_by_day"):
        save_top_k_analysis_to_db(
            top_k_analysis,
            top_k_table,
        )