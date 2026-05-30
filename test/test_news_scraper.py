from scrapping.news_scraper import (
    fetch_news,
    save_news_to_db,
    URLs
)


def test_fetch_news_success(mocker):
    fake_xml = """
    <rss>
      <channel>

        <item>
          <title>Oil prices surge</title>
          <link>https://example.com/article1</link>
          <pubDate>Fri, 23 May 2026</pubDate>
        </item>

        <item>
          <title>Iran tensions increase</title>
          <link>https://example.com/article2</link>
          <pubDate>Fri, 23 May 2026</pubDate>
        </item>

      </channel>
    </rss>
    """

    mock_response = mocker.Mock()
    mock_response.text = fake_xml

    mocked_get = mocker.patch(
        "scrapping.news_scraper.requests.get",
        return_value=mock_response
    )

    news = fetch_news()

    # Two items returned for each configured RSS URL
    assert len(news) == 2 * len(URLs)

    assert news[0]["title"] == "Oil prices surge"
    assert news[0]["link"] == "https://example.com/article1"
    assert news[0]["published"] == "Fri, 23 May 2026"

    assert news[1]["title"] == "Iran tensions increase"
    assert news[1]["link"] == "https://example.com/article2"
    assert news[1]["published"] == "Fri, 23 May 2026"

    assert mocked_get.call_count == len(URLs)


def test_fetch_news_failure(mocker):
    mocker.patch(
        "scrapping.news_scraper.requests.get",
        side_effect=Exception("Connection error")
    )

    news = fetch_news()

    assert news == []
    assert len(news) == 0


def test_fetch_news_empty(mocker):
    fake_xml = """
    <rss>
      <channel>
      </channel>
    </rss>
    """

    mock_response = mocker.Mock()
    mock_response.text = fake_xml

    mocked_get = mocker.patch(
        "scrapping.news_scraper.requests.get",
        return_value=mock_response
    )

    news = fetch_news()

    assert news == []
    assert len(news) == 0
    assert mocked_get.call_count == len(URLs)


def test_save_news_to_db(mocker):
    mock_table = mocker.Mock()

    news_list = [
        {
            "title": "Oil prices surge",
            "link": "https://example.com/article1",
            "published": "Fri, 23 May 2026"
        },
        {
            "title": "Iran tensions increase",
            "link": "https://example.com/article2",
            "published": "Fri, 23 May 2026"
        }
    ]

    save_news_to_db(news_list, mock_table)

    assert mock_table.insert.call_count == 2
    mock_table.insert.assert_any_call(news_list[0])
    mock_table.insert.assert_any_call(news_list[1])


def test_save_news_to_db_empty_list(mocker):
    mock_table = mocker.Mock()

    save_news_to_db([], mock_table)

    mock_table.insert.assert_not_called()