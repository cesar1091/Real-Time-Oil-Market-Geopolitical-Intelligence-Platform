from database.db import getDatabase, getSentimentTable, getNewsTable
from transformers import pipeline
from typing import List, Tuple
from datetime import datetime
import logging


logging.basicConfig(level=logging.INFO)
SENTIMENT_ANALYZER = pipeline("sentiment-analysis")

def fetch_sentiment_analysis()->List[Tuple[str, str, float]]:
    try:
        db = getDatabase()
        news_table = getNewsTable(db)
        news_data = news_table.all()
        sentiment_results = []
        for entry in news_data:
            text = entry.get('title')
            date = entry.get('published')
            parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S GMT")
            formatted_date = parsed_date.strftime("%d-%m-%Y")
            if text:
                result = SENTIMENT_ANALYZER(text[:512])
                sentiment_results.append((text, result[0]['label'], result[0]['score'], formatted_date))
        return sentiment_results
    except Exception as e:
        logging.error(f"Error performing sentiment analysis: {e}")
        return []
    
def save_sentiment_analysis_to_db(sentiment_results: List[Tuple[str, str, float, str]], sentiment_table):
    for text, label, score, date in sentiment_results:
        sentiment_table.insert({
            'text': text,
            'sentiment': label,
            'score': score,
            'published_date': date
        })
    logging.info(f"Inserted {len(sentiment_results)} sentiment analysis records into the database.")

if __name__ == "__main__":
    db = getDatabase()
    sentiment_table = getSentimentTable(db)
    sentiment_results = fetch_sentiment_analysis()
    if sentiment_results:
        save_sentiment_analysis_to_db(sentiment_results, sentiment_table)