# Real-Time Oil Market & Geopolitical Intelligence Platform

## Project Overview

This project aims to develop a real-time financial intelligence platform capable of monitoring oil market behavior and analyzing geopolitical events related to the Iran conflict. The platform combines live oil price tracking, web scraping, sentiment analysis, and predictive analytics to help users understand how international events and media narratives influence oil price volatility.

The main problem addressed by this project is the difficulty investors, analysts, and researchers face when trying to correlate geopolitical news with rapid changes in the energy market. Traditional financial dashboards typically focus only on historical market data and do not provide contextual intelligence regarding political events and public sentiment.

The platform is designed for:

* Financial analysts
* Investors
* Researchers
* Data scientists
* Organizations interested in energy market intelligence and geopolitical risk analysis

What makes this product unique is the integration of:

* Real-time oil market monitoring
* Automated web scraping of news and media statements
* Natural Language Processing (NLP) for sentiment analysis
* Machine learning models for trend prediction and anomaly detection
* Lightweight cloud-native deployment using free-tier infrastructure

Unlike conventional dashboards, this platform provides both quantitative and qualitative insights by combining market data with geopolitical information streams.

---

# High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      End Users       │
                         │ Investors / Analysts │
                         └──────────┬───────────┘
                                    │
                                    ▼
                   ┌─────────────────────────────────┐
                   │        Front-End Dashboard      │
                   │ Streamlit Community Cloud       │
                   │ - Oil price monitoring          │
                   │ - News visualization            │
                   │ - Sentiment analytics           │
                   └────────────────┬────────────────┘
                                    │ REST API
                                    ▼
                   ┌─────────────────────────────────┐
                   │        Back-End API             │
                   │ FastAPI + Python                │
                   │ Hosted on Render/Railway        │
                   └────────────────┬────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼

┌─────────────────┐      ┌──────────────────────┐     ┌────────────────────┐
│ Financial APIs  │      │ Web Scraping Engine  │     │ ML/NLP Models      │
│ yfinance        │      │ News websites        │     │ Sentiment analysis  │
│ Alpha Vantage   │      │ Iran conflict news   │     │ Trend prediction    │
└────────┬────────┘      └──────────┬───────────┘     └─────────┬──────────┘
         │                           │                           │
         └───────────────┬───────────┴───────────────┬──────────┘
                         ▼                           ▼

               ┌──────────────────────────────────────┐
               │ Lightweight Data Storage             │
               │ GitHub + CSV/JSON + SQLite           │
               │ - Historical prices                  │
               │ - Scraped news                       │
               │ - Sentiment outputs                  │
               └──────────────────────────────────────┘

                         ▼
               ┌──────────────────────────────────────┐
               │ CI/CD Pipeline                       │
               │ GitHub Actions                       │
               │ - Automated testing                  │
               │ - Scraping scheduler                 │
               │ - Auto deployment                    │
               └──────────────────────────────────────┘
```

---

# Technology Stack

## Front-End

* Streamlit

## Back-End

* FastAPI
* Python

## Data Collection

* yfinance
* BeautifulSoup
* Requests

## Machine Learning & NLP

* Hugging Face Transformers
* TextBlob / VADER
* Scikit-learn

## Storage

* SQLite
* CSV / JSON files

## DevOps & CI/CD

* GitHub
* GitHub Actions

## Deployment

* Streamlit Community Cloud
* Render / Railway

---

# Key Features

* Real-time oil price monitoring
* Automated news scraping
* Geopolitical event tracking
* Sentiment analysis on news articles
* Trend prediction and anomaly detection
* Lightweight cloud deployment
* Automated CI/CD pipelines
* Free-tier infrastructure usage

---

# Future Improvements

* Real-time WebSocket streaming
* Kafka-based event pipelines
* Advanced transformer-based forecasting
* Interactive alert system
* Integration with additional financial markets
* Multi-language news analysis
