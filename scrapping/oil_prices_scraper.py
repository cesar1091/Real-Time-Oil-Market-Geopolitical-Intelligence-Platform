import yfinance as yf
import pandas as pd
from database.db import getDatabase, getOilTable
import logging
from typing import List, Dict
from tinydb.table import Table

logging.basicConfig(level=logging.INFO)

TICKERS = ['CL=F', 'BZ=F', 'NG=F']

def fetch_oil_prices()-> List[Dict]:
    try:
        data = yf.download(TICKERS, period='5d', interval='1h')
        if data.empty:
            logging.warning("No data fetched for the given tickers.")
            return []
        
        oil_prices_list = []

        for ticker in TICKERS:
            ticker_data = data.xs(
                ticker,
                axis=1,
                level=1
            )
            logging.info(f"Data for {ticker}: {ticker_data.shape[0]} rows")
            
            for index, row in ticker_data.iterrows():
                oil_prices_list.append({
                    'ticker': ticker,
                    'datetime': index.isoformat(),
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'volume': row['Volume']
                })
        logging.info(
            f"Retrieved {len(oil_prices_list)} oil price records."
        )
        return oil_prices_list
    
    except Exception as e:
        logging.error(f"Error fetching oil prices: {e}")
        return []

def save_oil_prices_to_db(oil_prices_list: List[Dict], oil_table: Table) -> None:
    for price in oil_prices_list:
        oil_table.insert(price)
    logging.info(f"Inserted {len(oil_prices_list)} oil price records into the database.")

if __name__ == "__main__":
    db = getDatabase()
    oil_table = getOilTable(db)
    oil_prices_list = fetch_oil_prices()
    if oil_prices_list:
        save_oil_prices_to_db(oil_prices_list, oil_table)