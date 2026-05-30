from tinydb import TinyDB
import os
import json

def getDatabase(path: str = "data/scraping_data.json") -> TinyDB:
    # Create file if doesn't exist
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

    # Fix empty file
    if os.path.getsize(path) == 0:
        with open(path, "w") as f:
            json.dump({}, f)
    return TinyDB(path)

def resetDatabase(path: str = "data/scraping_data.json") -> None:
    with open(path, "w") as f:
        json.dump({}, f)

def getNewsTable(db: TinyDB) -> TinyDB.table:
    return db.table("news")

def getOilTable(db: TinyDB) -> TinyDB.table:
    return db.table("oil_prices")

def getSentimentTable(db: TinyDB) -> TinyDB.table:
    return db.table("sentiment")

def getTopKTable(db: TinyDB) -> TinyDB.table:
    return db.table("top_k_analysis")

def getCorrelationTable(db: TinyDB) -> TinyDB.table:
    return db.table("correlation_analysis")

