#!/usr/bin/env python3
from flask import Flask, request, render_template
from database.db import getDatabase, getNewsTable, getOilTable, getSentimentTable
import spacy
from transformers import pipeline

TICKERS = ['CL=F', 'BZ=F', 'NG=F']
app = Flask(__name__, static_folder="static", template_folder="templates")
NLP = spacy.load("en_core_web_sm")


@app.route("/", methods=["GET", "POST"])
def main():
    response_text = None
    if request.method == "POST":
        input_text = request.form.get("user_input", "").strip()
        response_text = (
            "You entered: " + input_text
            if input_text
            else "Please enter a query to get intelligence feedback."
        )
    return render_template("index.html", response_text=response_text)

@app.route("/oilanalytics")
def oil_analytics():
    db = getDatabase()
    oil_table = getOilTable(db)
    oil_data = oil_table.all()
    # Placeholder for processing the data and generating insights
    insights = {}
    for ticker in TICKERS:
        ticker_data = [entry for entry in oil_data if entry['ticker'] == ticker]
        # Process ticker_data to calculate insights (e.g., average price, trends)
        if ticker_data:
            average_price = sum(entry['close'] for entry in ticker_data) / len(ticker_data)
            max_price = max(entry['high'] for entry in ticker_data)
            min_price = min(entry['low'] for entry in ticker_data)
            std_price = (sum((entry['close'] - average_price) ** 2 for entry in ticker_data) / len(ticker_data)) ** 0.5
            insights[ticker] = {
                'average_price': average_price,
                'max_price': max_price,
                'min_price': min_price,
                'std_price': std_price,
                'data_points': len(ticker_data)
            }
        else:
            insights[ticker] = {
                'average_price': None,
                'max_price': None,
                'min_price': None,
                'std_price': None,
                'data_points': 0
            }
    return insights

@app.route("/topNnewskeywords/<int:n>")
def news_analytics(n):
    db = getDatabase()
    news_table = getNewsTable(db)
    news_data = news_table.all()
    # Depurate titles to extract keywords and count their occurrences
    # Placeholder for processing the data and generating insights
    keyword_counts = {}
    for entry in news_data:
        title = entry.get('title', '')
        doc = NLP(title)
        keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop]
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:n]
    return {"top_keywords": top_keywords}

@app.route("averageSentimentreport/<start_date>/<end_date>")
def sentiment_report(start_date, end_date):
    # Implementation for fetching and calculating average sentiment within a date range
    db = getDatabase()
    sentiment_table = getSentimentTable(db)
    sentiment_data = sentiment_table.all()
    # Filter sentiment_data based on the provided date range and calculate average sentiment    
    filtered_data = [entry for entry in sentiment_data if start_date <= entry['published_date'] <= end_date]
    if not filtered_data:
        return {"average_sentiment": None, "message": "No sentiment data available for the specified date range."}
    average_sentiment = sum(entry['score'] for entry in filtered_data) / len(filtered_data)
    # Count how many entries are positive, negative, and neutral
    sentiment_counts = {
        'positive': sum(1 for entry in filtered_data if entry['sentiment'] == 'POSITIVE'),
        'negative': sum(1 for entry in filtered_data if entry['sentiment'] == 'NEGATIVE'),
        'neutral': sum(1 for entry in filtered_data if entry['sentiment'] == 'NEUTRAL')
    }.sort(key=lambda x: x[1], reverse=True)
    return {"average_sentiment": average_sentiment, "message": "Sentiment data calculated for the specified date range.", "sentiment_counts": sentiment_counts}
