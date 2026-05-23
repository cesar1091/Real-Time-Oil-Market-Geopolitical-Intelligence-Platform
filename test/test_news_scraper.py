from scrapping.news_scraper import fetch_news

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
    mocker.patch('scrapping.news_scraper.requests.get', 
                 return_value=mock_response)
    news = fetch_news()
    assert len(news) == 2
    assert news[0]['title'] == "Oil prices surge"
    assert news[0]['link'] == "https://example.com/article1"
    assert news[0]['published'] == "Fri, 23 May 2026"
    assert news[1]['title'] == "Iran tensions increase"
    assert news[1]['link'] == "https://example.com/article2"
    assert news[1]['published'] == "Fri, 23 May 2026"

def test_fetch_news_failure(mocker):
    mocker.patch('scrapping.news_scraper.requests.get', 
                 side_effect=Exception("Connection error"))
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
    mocker.patch('scrapping.news_scraper.requests.get', 
                 return_value=mock_response)
    news = fetch_news()
    assert news == []
    assert len(news) == 0