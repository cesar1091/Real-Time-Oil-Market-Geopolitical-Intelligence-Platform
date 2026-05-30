from database.db import *
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


def perform_correlation_analysis() -> dict:
    try:
        db = getDatabase()

        # use the main oil table (tests patch getOilTable)
        oil_table = getOilTable(db)
        sentiment_table = getSentimentTable(db)

        oil_data = oil_table.all()
        sentiment_data = sentiment_table.all()

        if not oil_data:
            return {
                "correlation": None,
                "message": "No oil data found."
            }

        if not sentiment_data:
            return {
                "correlation": None,
                "message": "No sentiment data found."
            }

        oil_df = pd.DataFrame(oil_data)
        sentiment_df = pd.DataFrame(sentiment_data)

        logging.info(f"Oil records: {len(oil_df)}")
        logging.info(f"Sentiment negative records: {len(sentiment_df)}")

        # Map/validate oil columns. Support either the test fixtures (datetime/close)
        # or the prior schema (date/average_close).
        if "datetime" in oil_df.columns and "close" in oil_df.columns:
            oil_df = oil_df.rename(columns={"datetime": "date", "close": "average_close"})
        elif "date" in oil_df.columns and "close" in oil_df.columns:
            oil_df = oil_df.rename(columns={"close": "average_close"})

        required_oil_columns = {"date", "average_close"}
        required_sentiment_columns = {"published_date", "score"}

        if not required_oil_columns.issubset(set(oil_df.columns)):
            return {
                "correlation": None,
                "error": f"missing columns: {required_oil_columns - set(oil_df.columns)}"
            }

        if not required_sentiment_columns.issubset(set(sentiment_df.columns)):
            return {
                "correlation": None,
                "error": f"missing columns: {required_sentiment_columns - set(sentiment_df.columns)}"
            }

        # Convert oil timestamps to daily dates
        oil_df["date_key"] = (
            pd.to_datetime(
                oil_df["date"],
                utc=True,
                errors="coerce"
            )
            .dt.date
        )

        # Convert sentiment dates (dd-mm-yyyy)
        sentiment_df["date_key"] = (
            pd.to_datetime(
                sentiment_df["published_date"],
                dayfirst=True,
                errors="coerce"
            )
            .dt.date
        )

        # Remove invalid dates
        oil_df = oil_df.dropna(subset=["date_key", "average_close"])
        sentiment_df = sentiment_df.dropna(subset=["date_key", "score"])

        # Aggregate sentiment by day
        daily_sentiment = (
            sentiment_df
            .groupby("date_key", as_index=False)["score"]
            .mean()
        )

        # Merge on date
        merged_df = pd.merge(
            oil_df,
            daily_sentiment,
            on="date_key",
            how="inner"
        )

        logging.info(f"Overlapping dates: {len(merged_df)}")

        if len(merged_df) < 2:
            return {
                "correlation": None,
                "message": "Not enough overlapping dates to calculate correlation.",
                "overlapping_dates": len(merged_df)
            }

        correlation = merged_df["average_close"].corr(
            merged_df["score"]
        )

        return {
            "correlation": round(float(correlation), 4),
            "records_used": len(merged_df),
            "oil_days": len(oil_df),
            "sentiment_days": len(daily_sentiment),
            "date_range": {
                "start": str(merged_df["date_key"].min()),
                "end": str(merged_df["date_key"].max())
            }
        }

    except Exception as e:
        logging.exception("Error performing correlation analysis")

        return {
            "correlation": None,
            "error": str(e)
        }
    
def save_correlation_analysis_to_db(correlation_result: dict, correlation_table):
    correlation_table.insert(correlation_result)
    logging.info("Inserted correlation analysis result into the database.")


if __name__ == "__main__":
    db = getDatabase()
    correlation_table = getCorrelationTable(db)
    correlation_table.truncate()  # optional: clear previous results
    result = perform_correlation_analysis()
    if result.get("correlation") is not None:
        save_correlation_analysis_to_db(result, correlation_table)
    