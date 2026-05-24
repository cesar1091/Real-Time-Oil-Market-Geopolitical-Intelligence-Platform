# test_sentiment_analysis.py

from unittest.mock import patch, MagicMock
from analytics.sentiment_analysis import (
    fetch_sentiment_analysis,
    save_sentiment_analysis_to_db
)

# -----------------------------
# Test fetch_sentiment_analysis
# -----------------------------

@patch("analytics.sentiment_analysis.SENTIMENT_ANALYZER")
@patch("analytics.sentiment_analysis.getNewsTable")
@patch("analytics.sentiment_analysis.getDatabase")
def test_fetch_sentiment_analysis_success(
    mock_get_db,
    mock_get_news_table,
    mock_sentiment_analyzer
):
    # Mock database and table
    mock_db = MagicMock()
    mock_table = MagicMock()

    mock_get_db.return_value = mock_db
    mock_get_news_table.return_value = mock_table

    # Mock news data
    mock_table.all.return_value = [
        {
            "title": "Oil prices increase after OPEC meeting",
            "published": "Mon, 20 May 2024 10:00:00 GMT"
        }
    ]

    # Mock sentiment pipeline response
    mock_sentiment_analyzer.return_value = [
        {
            "label": "POSITIVE",
            "score": 0.98
        }
    ]

    result = fetch_sentiment_analysis()

    expected = [
        (
            "Oil prices increase after OPEC meeting",
            "POSITIVE",
            0.98,
            "20-05-2024"
        )
    ]

    assert result == expected


@patch("analytics.sentiment_analysis.getNewsTable")
@patch("analytics.sentiment_analysis.getDatabase")
def test_fetch_sentiment_analysis_exception(
    mock_get_db,
    mock_get_news_table
):
    # Simulate exception
    mock_get_news_table.side_effect = Exception("DB error")

    result = fetch_sentiment_analysis()

    assert result == []


# -----------------------------------
# Test save_sentiment_analysis_to_db
# -----------------------------------

def test_save_sentiment_analysis_to_db():
    mock_table = MagicMock()

    sentiment_results = [
        (
            "Market crashes due to inflation fears",
            "NEGATIVE",
            0.91,
            "21-05-2024"
        )
    ]

    save_sentiment_analysis_to_db(sentiment_results, mock_table)

    mock_table.insert.assert_called_once_with({
        "text": "Market crashes due to inflation fears",
        "sentiment": "NEGATIVE",
        "score": 0.91,
        "published_date": "21-05-2024"
    })


def test_save_sentiment_analysis_to_db_multiple_records():
    mock_table = MagicMock()

    sentiment_results = [
        ("News 1", "POSITIVE", 0.95, "20-05-2024"),
        ("News 2", "NEGATIVE", 0.88, "21-05-2024")
    ]

    save_sentiment_analysis_to_db(sentiment_results, mock_table)

    assert mock_table.insert.call_count == 2