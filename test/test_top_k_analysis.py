from unittest.mock import Mock, patch

from analytics.top_k_analysis import (
    _extract_keywords,
    fetch_news_analytics,
    save_top_k_analysis_to_db,
)


class FakeTable:
    def __init__(self, data):
        self._data = data

    def all(self):
        return self._data


def test_extract_keywords_returns_list():
    result = _extract_keywords(
        "Iran oil exports increase significantly"
    )

    assert isinstance(result, list)
    assert len(result) > 0


def test_fetch_news_analytics_success():
    news_data = [
        {
            "title": "Iran oil exports increase",
            "published": "Fri, 23 May 2026 10:00:00 GMT",
        },
        {
            "title": "Oil prices surge",
            "published": "Fri, 23 May 2026 12:00:00 GMT",
        },
        {
            "title": "Trump comments on oil market",
            "published": "Sat, 24 May 2026 10:00:00 GMT",
        },
    ]

    news_table = FakeTable(news_data)

    with patch(
        "analytics.top_k_analysis.getDatabase"
    ), patch(
        "analytics.top_k_analysis.getNewsTable",
        return_value=news_table,
    ):
        result = fetch_news_analytics()

    assert "top_keywords_by_day" in result

    days = result["top_keywords_by_day"]

    assert "23-05-2026" in days
    assert "24-05-2026" in days

    assert isinstance(days["23-05-2026"], list)
    assert isinstance(days["24-05-2026"], list)


def test_fetch_news_analytics_invalid_date():
    news_data = [
        {
            "title": "Iran oil exports increase",
            "published": "invalid-date",
        }
    ]

    news_table = FakeTable(news_data)

    with patch(
        "analytics.top_k_analysis.getDatabase"
    ), patch(
        "analytics.top_k_analysis.getNewsTable",
        return_value=news_table,
    ):
        result = fetch_news_analytics()

    assert "unknown" in result["top_keywords_by_day"]


def test_fetch_news_analytics_empty_table():
    news_table = FakeTable([])

    with patch(
        "analytics.top_k_analysis.getDatabase"
    ), patch(
        "analytics.top_k_analysis.getNewsTable",
        return_value=news_table,
    ):
        result = fetch_news_analytics()

    assert result == {
        "top_keywords_by_day": {}
    }


def test_fetch_news_analytics_database_error():
    with patch(
        "analytics.top_k_analysis.getDatabase",
        side_effect=Exception("Database failure"),
    ):
        result = fetch_news_analytics()

    assert result == {
        "top_keywords_by_day": {}
    }


def test_save_top_k_analysis_to_db():
    mock_table = Mock()

    analysis = {
        "top_keywords_by_day": {
            "23-05-2026": [
                ("oil", 5),
                ("iran", 3),
            ],
            "24-05-2026": [
                ("trump", 4),
            ],
        }
    }

    save_top_k_analysis_to_db(
        analysis,
        mock_table,
    )

    mock_table.truncate.assert_called_once()

    assert mock_table.insert.call_count == 2

    mock_table.insert.assert_any_call(
        {
            "date": "23-05-2026",
            "top_keywords": [
                ("oil", 5),
                ("iran", 3),
            ],
        }
    )

    mock_table.insert.assert_any_call(
        {
            "date": "24-05-2026",
            "top_keywords": [
                ("trump", 4),
            ],
        }
    )


def test_save_top_k_analysis_to_db_empty():
    mock_table = Mock()

    analysis = {
        "top_keywords_by_day": {}
    }

    save_top_k_analysis_to_db(
        analysis,
        mock_table,
    )

    mock_table.truncate.assert_called_once()
    mock_table.insert.assert_not_called()