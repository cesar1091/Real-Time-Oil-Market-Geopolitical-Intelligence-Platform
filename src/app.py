#!/usr/bin/env python3
from flask import Flask, request, render_template
from database.db import *

TICKERS = ['CL=F', 'BZ=F', 'NG=F']
app = Flask(__name__, static_folder="static", template_folder="templates")

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

@app.route("/oilanalytics/<string:ticker>")
def oil_analytics(ticker):
    db = getDatabase()
    oil_table = getOilTable(db)
    oil_data = oil_table.all()
    # Placeholder for processing the data and generating insights
    insights = {}
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

@app.route("/topNnewskeywords/<string:day>/<int:n>")
def news_analytics(day, n):
    db = getDatabase()
    top_keywords = getTopKTable(db)
    top_keywords_data = top_keywords.all()
    # Depurate titles to extract keywords and count their occurrences
    # Placeholder for processing the data and generating insights
    day_keywords = [entry for entry in top_keywords_data if entry['date'] == day]
    if day_keywords:
        entries = day_keywords[0]['top_keywords']
        top_n_keywords = entries[:n]
        return {"date": day, "top_n_keywords": top_n_keywords}
    else:
        return {"date": day, "top_n_keywords": []}
    
        

@app.route("/averageSentimentreport/<start_date>/<end_date>")
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
    }
    return {"average_sentiment": average_sentiment, "message": "Sentiment data calculated for the specified date range.", "sentiment_counts": sentiment_counts}

@app.route("/correlationreport")
def correlation_report():
    # Implementation for calculating correlation between oil prices and news sentiment
    db = getDatabase()
    correlation_report = getCorrelationTable(db)
    correlation_data = correlation_report.all()
    # Placeholder for processing the data and calculating correlation
    if correlation_data:
        return {"correlation_report": correlation_data[0]}  # Assuming there's only one report entry
    else:
        return {"correlation_report": None, "message": "No correlation data available."}
