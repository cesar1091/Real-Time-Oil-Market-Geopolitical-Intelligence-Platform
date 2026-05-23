import requests
from bs4 import BeautifulSoup
from database.db import getDatabase, getNewsTable
import logging
from typing import List, Dict
from tinydb.table import Table

logging.basicConfig(level=logging.INFO)
URL = "https://news.google.com/rss/search?q=iran+oil"

def fetch_news() -> List[Dict[str, str]]:
    try:
        response = requests.get(URL)
        # Parse XML
        soup = BeautifulSoup(response.text, "xml")
        # Find all news items
        items = soup.find_all("item")
        # Save news items
        newsList = []
        for item in items:
            title = item.title.text
            link = item.link.text
            pub_date = item.pubDate.text
            newsList.append({
                'title': title,
                'link': link,
                'published': pub_date
            })

        return newsList
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return []

def save_news_to_db(newsList: List[Dict[str, str]], news_table: Table) -> None:
    for news in newsList:
        news_table.insert(news)
    logging.info(f"Inserted {len(newsList)} news items into the database.")

if __name__ == "__main__":
    db = getDatabase()
    news_table = getNewsTable(db)
    newsList = fetch_news()
    if newsList:
        save_news_to_db(newsList, news_table)