#!/usr/bin/env python3
from flask import Flask, request, render_template
from database.db import *
from datetime import datetime

TICKERS = ['CL=F', 'BZ=F', 'NG=F']
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def main():
    # Project description shown by default on GET
    project_description = (
        "Real-Time Oil Market Geopolitical Intelligence Platform: collects news and oil-price data, "
        "runs sentiment and correlation analysis, and exposes dashboards and APIs for exploration. "
        "Use the Analytics Dashboard link below to view top keywords, sentiment trends and correlation reports."
    )

    response_text = project_description
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


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/top_keywords_by_day")
def api_top_keywords_by_day():
    db = getDatabase()
    top_k_table = getTopKTable(db)
    entries = top_k_table.all()

    start = request.args.get('start_date')
    end = request.args.get('end_date')

    def in_range(d):
        if d == 'unknown':
            return False
        try:
            dd = datetime.strptime(d, "%d-%m-%Y")
        except Exception:
            return False
        if start:
            try:
                s = datetime.strptime(start, "%d-%m-%Y")
                if dd < s:
                    return False
            except Exception:
                pass
        if end:
            try:
                e = datetime.strptime(end, "%d-%m-%Y")
                if dd > e:
                    return False
            except Exception:
                pass
        return True

    result = {}
    for e in entries:
        date = e.get('date', 'unknown')
        if start or end:
            if not in_range(date):
                continue
        result[date] = e.get('top_keywords', [])
    return {"top_keywords_by_day": result}


@app.route("/api/sentiment_by_day")
def api_sentiment_by_day():
    db = getDatabase()
    sentiment_table = getSentimentTable(db)
    entries = sentiment_table.all()
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    def in_range(d):
        if d == 'unknown':
            return False
        try:
            dd = datetime.strptime(d, "%d-%m-%Y")
        except Exception:
            return False
        if start:
            try:
                s = datetime.strptime(start, "%d-%m-%Y")
                if dd < s:
                    return False
            except Exception:
                pass
        if end:
            try:
                e = datetime.strptime(end, "%d-%m-%Y")
                if dd > e:
                    return False
            except Exception:
                pass
        return True

    sums = {}
    counts = {}
    for e in entries:
        if e.get('sentiment')=='NEGATIVE':
            d = e.get('published_date', 'unknown')
            if start or end:
                if not in_range(d):
                    continue
            s = e.get('score', 0)
            sums[d] = sums.get(d, 0) + s
            counts[d] = counts.get(d, 0) + 1
    avg = {d: (sums[d] / counts[d]) for d in sums}
    return {"sentiment_by_day": avg}


@app.route("/api/sentiment_counts_by_day")
def api_sentiment_counts_by_day():
    db = getDatabase()
    sentiment_table = getSentimentTable(db)
    entries = sentiment_table.all()
    # order entries by published_date ascending, treating missing or invalid dates as 'unknown' which will be sorted at the end
    entries.sort(key=lambda x: x.get('published_date', 'unknown'))
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    def in_range(d):
        if d == 'unknown':
            return False
        try:
            dd = datetime.strptime(d, "%d-%m-%Y")
        except Exception:
            return False
        if start:
            try:
                s = datetime.strptime(start, "%d-%m-%Y")
                if dd < s:
                    return False
            except Exception:
                pass
        if end:
            try:
                e = datetime.strptime(end, "%d-%m-%Y")
                if dd > e:
                    return False
            except Exception:
                pass
        return True

    counts_by_day = {}
    for e in entries:
        d = e.get('published_date', 'unknown')
        if start or end:
            if not in_range(d):
                continue
        label = e.get('sentiment', 'UNKNOWN').upper()
        if d not in counts_by_day:
            counts_by_day[d] = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0, 'UNKNOWN': 0}
        if label not in counts_by_day[d]:
            counts_by_day[d][label] = 0
        counts_by_day[d][label] += 1

    return {"sentiment_counts_by_day": counts_by_day}


@app.route("/api/average_oil_price")
def api_average_oil_price():
    db = getDatabase()
    analysis_table = getOilAnalysisTable(db)
    entries = analysis_table.all()
    start = request.args.get('start_date')
    end = request.args.get('end_date')

    start_date = None
    end_date = None
    if start:
        try:
            start_date = datetime.strptime(start, "%d-%m-%Y").date()
        except Exception:
            start_date = None
    if end:
        try:
            end_date = datetime.strptime(end, "%d-%m-%Y").date()
        except Exception:
            end_date = None

    daily_ticker_values = {}
    ticker_sums = {}
    ticker_counts = {}
    total_sum = 0
    total_count = 0

    for entry in entries:
        day = entry.get('date')
        ticker = entry.get('ticker', 'unknown')
        price = entry.get('average_close')
        if not day or price is None:
            continue

        try:
            record_date = datetime.strptime(day, "%d-%m-%Y").date()
        except Exception:
            continue
        if start_date and record_date < start_date:
            continue
        if end_date and record_date > end_date:
            continue

        if day not in daily_ticker_values:
            daily_ticker_values[day] = {}
        daily_ticker_values[day][ticker] = price

        ticker_sums[ticker] = ticker_sums.get(ticker, 0) + price
        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        total_sum += price
        total_count += 1

    daily_average = {
        day: sum(ticker_prices.values()) / len(ticker_prices)
        for day, ticker_prices in daily_ticker_values.items()
        if ticker_prices
    }
    average_by_ticker = {
        ticker: (ticker_sums[ticker] / ticker_counts[ticker])
        for ticker in ticker_sums
        if ticker_counts[ticker]
    }
    overall = total_sum / total_count if total_count else None

    return {
        "average_price": {
            "overall": overall,
            "by_ticker": average_by_ticker,
            "daily_average": daily_average,
            "daily_ticker_average": daily_ticker_values
        }
    }


@app.route("/api/correlation")
def api_correlation():
    db = getDatabase()
    correlation_table = getCorrelationTable(db)
    entries = correlation_table.all()
    return {"correlation": entries}
