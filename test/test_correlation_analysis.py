import pytest
from unittest.mock import Mock, patch

from analytics.correlation_analysis import (
    perform_correlation_analysis,
    save_correlation_analysis_to_db,
)


class FakeTable:
    def __init__(self, data):
        self._data = data

    def all(self):
        return self._data


def test_no_oil_data():
    oil_table = FakeTable([])
    sentiment_table = FakeTable([
        {
            "published_date": "01-01-2025",
            "score": 0.5,
        }
    ])

    with patch(
        "analytics.correlation_analysis.getDatabase"
    ), patch(
        "analytics.correlation_analysis.getOilTable",
        return_value=oil_table,
    ), patch(
        "analytics.correlation_analysis.getSentimentTable",
        return_value=sentiment_table,
    ):
        result = perform_correlation_analysis()

    assert result["correlation"] is None
    assert result["message"] == "No oil data found."


def test_no_sentiment_data():
    oil_table = FakeTable([
        {
            "datetime": "2025-01-01T00:00:00Z",
            "close": 70.0,
        }
    ])

    sentiment_table = FakeTable([])

    with patch(
        "analytics.correlation_analysis.getDatabase"
    ), patch(
        "analytics.correlation_analysis.getOilTable",
        return_value=oil_table,
    ), patch(
        "analytics.correlation_analysis.getSentimentTable",
        return_value=sentiment_table,
    ):
        result = perform_correlation_analysis()

    assert result["correlation"] is None
    assert result["message"] == "No sentiment data found."


def test_missing_oil_columns():
    oil_table = FakeTable([
        {
            "price": 70.0
        }
    ])

    sentiment_table = FakeTable([
        {
            "published_date": "01-01-2025",
            "score": 0.5,
        }
    ])

    with patch(
        "analytics.correlation_analysis.getDatabase"
    ), patch(
        "analytics.correlation_analysis.getOilTable",
        return_value=oil_table,
    ), patch(
        "analytics.correlation_analysis.getSentimentTable",
        return_value=sentiment_table,
    ):
        result = perform_correlation_analysis()

    assert result["correlation"] is None
    assert "missing columns" in result["error"]


def test_missing_sentiment_columns():
    oil_table = FakeTable([
        {
            "datetime": "2025-01-01T00:00:00Z",
            "close": 70.0,
        }
    ])

    sentiment_table = FakeTable([
        {
            "sentiment": "positive"
        }
    ])

    with patch(
        "analytics.correlation_analysis.getDatabase"
    ), patch(
        "analytics.correlation_analysis.getOilTable",
        return_value=oil_table,
    ), patch(
        "analytics.correlation_analysis.getSentimentTable",
        return_value=sentiment_table,
    ):
        result = perform_correlation_analysis()

    assert result["correlation"] is None
    assert "missing columns" in result["error"]


def test_not_enough_overlapping_dates():
    oil_table = FakeTable([
        {
            "datetime": "2025-01-01T00:00:00Z",
            "close": 70.0,
        }
    ])

    sentiment_table = FakeTable([
        {
            "published_date": "02-01-2025",
            "score": 0.5,
        }
    ])

    with patch(
        "analytics.correlation_analysis.getDatabase"
    ), patch(
        "analytics.correlation_analysis.getOilTable",
        return_value=oil_table,
    ), patch(
        "analytics.correlation_analysis.getSentimentTable",
        return_value=sentiment_table,
    ):
        result = perform_correlation_analysis()

    assert result["correlation"] is None
    assert (
        result["message"]
        == "Not enough overlapping dates to calculate correlation."
    )


def test_successful_correlation():
    oil_table = FakeTable([
        {
            "datetime": "2025-01-01T00:00:00Z",
            "close": 70.0,
        },
        {
            "datetime": "2025-01-02T00:00:00Z",
            "close": 80.0,
        },
        {
            "datetime": "2025-01-03T00:00:00Z",
            "close": 90.0,
        },
    ])

    sentiment_table = FakeTable([
        {
            "published_date": "01-01-2025",
            "score": 1.0,
        },
        {
            "published_date": "02-01-2025",
            "score": 2.0,
        },
        {
            "published_date": "03-01-2025",
            "score": 3.0,
        },
    ])

    with patch(
        "analytics.correlation_analysis.getDatabase"
    ), patch(
        "analytics.correlation_analysis.getOilTable",
        return_value=oil_table,
    ), patch(
        "analytics.correlation_analysis.getSentimentTable",
        return_value=sentiment_table,
    ):
        result = perform_correlation_analysis()

    assert result["correlation"] == pytest.approx(1.0)
    assert result["records_used"] == 3
    assert result["oil_days"] == 3
    assert result["sentiment_days"] == 3


def test_save_correlation_analysis_to_db():
    table = Mock()

    result = {
        "correlation": 0.85,
        "records_used": 10,
    }

    save_correlation_analysis_to_db(result, table)

    table.insert.assert_called_once_with(result)