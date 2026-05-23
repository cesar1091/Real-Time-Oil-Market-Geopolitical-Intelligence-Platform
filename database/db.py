from tinydb import TinyDB

def getDatabase(path: str = "data/scraping_data.json") -> TinyDB:
    return TinyDB(path)

def getNewsTable(db: TinyDB) -> TinyDB.table:
    return db.table("news")

def getOilTable(db: TinyDB) -> TinyDB.table:
    return db.table("oil_prices")

def getSentimentTable(db: TinyDB) -> TinyDB.table:
    return db.table("sentiment")
