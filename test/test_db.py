from database.db import getDatabase, getNewsTable, getOilTable, getSentimentTable
from tinydb import TinyDB
from tinydb.table import Table

def test_getDatabase():
    db = getDatabase()
    assert isinstance(db, TinyDB)

def test_getNewsTable():
    db = getDatabase()
    news_table = getNewsTable(db)
    assert news_table.name == "news"
    assert isinstance(news_table, Table)

def test_getOilTable():
    db = getDatabase()
    oil_table = getOilTable(db)
    assert oil_table.name == "oil_prices"
    assert isinstance(oil_table, Table)

def test_getSentimentTable():
    db = getDatabase()
    sentiment_table = getSentimentTable(db)
    assert sentiment_table.name == "sentiment"
    assert isinstance(sentiment_table, Table)