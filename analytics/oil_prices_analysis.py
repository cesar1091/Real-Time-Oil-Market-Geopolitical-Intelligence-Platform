from database.db import *
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


def oil_prices_analysis() -> dict:
    try:
        db = getDatabase()
        oil_table = getOilTable(db)

        oil_data = oil_table.all()

        if not oil_data:
            return {
                "daily_average_prices": [],
                "message": "No oil price data found."
            }

        oil_df = pd.DataFrame(oil_data)

        required_columns = {"datetime", "ticker", "close"}

        if not required_columns.issubset(oil_df.columns):
            return {
                "daily_average_prices": [],
                "error": (
                    f"Missing columns: "
                    f"{required_columns - set(oil_df.columns)}"
                )
            }

        oil_df["datetime"] = pd.to_datetime(
            oil_df["datetime"],
            errors="coerce",
            utc=True
        )

        oil_df = oil_df.dropna(
            subset=["datetime", "ticker", "close"]
        )

        oil_df["date"] = oil_df["datetime"].dt.strftime(
            "%d-%m-%Y"
        )

        daily_avg_price = (
            oil_df
            .groupby(["date", "ticker"], as_index=False)["close"]
            .mean()
            .rename(columns={"close": "average_close"})
        )

        result = daily_avg_price.to_dict(
            orient="records"
        )

        return {
            "daily_average_prices": result,
            "records_generated": len(result)
        }

    except Exception as e:
        logging.exception(
            "Error during oil prices analysis"
        )

        return {
            "daily_average_prices": [],
            "error": str(e)
        }


def save_oil_prices_analysis_to_db(
    analysis_result: dict,
    oil_analysis_table
):
    oil_analysis_table.truncate()

    records = analysis_result.get(
        "daily_average_prices",
        []
    )

    for record in records:
        oil_analysis_table.insert(record)

    logging.info(
        "Inserted %d oil price analysis records.",
        len(records)
    )


if __name__ == "__main__":
    db = getDatabase()

    oil_analysis_table = getOilAnalysisTable(db)

    analysis_result = oil_prices_analysis()

    if analysis_result.get(
        "daily_average_prices"
    ):
        save_oil_prices_analysis_to_db(
            analysis_result,
            oil_analysis_table
        )

        logging.info(
            "Oil prices analysis completed successfully."
        )
    else:
        logging.warning(
            "No oil prices analysis records generated."
        )